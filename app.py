import base64
import cv2
import json
import numpy as np
import os
import requests

from flask import Flask, jsonify, render_template, request, session
from io import BytesIO
from keras.models import model_from_json
from keras.utils import img_to_array

app = Flask(__name__)
app.secret_key = "secret_key"
app.config["UPLOAD_FOLDER"] = "static/uploads"


def handle_4xx_error(e):
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]
    return render_template("4xx_error.html", options=options), e.code


def handle_5xx_error(e):
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]
    return render_template("5xx_error.html", options=options), e.code


app.register_error_handler(400, handle_4xx_error)
app.register_error_handler(401, handle_4xx_error)
app.register_error_handler(403, handle_4xx_error)
app.register_error_handler(404, handle_4xx_error)
app.register_error_handler(405, handle_4xx_error)
app.register_error_handler(406, handle_4xx_error)
app.register_error_handler(408, handle_4xx_error)
app.register_error_handler(409, handle_4xx_error)
app.register_error_handler(410, handle_4xx_error)
app.register_error_handler(412, handle_4xx_error)
app.register_error_handler(416, handle_4xx_error)
app.register_error_handler(417, handle_4xx_error)
app.register_error_handler(422, handle_4xx_error)
app.register_error_handler(423, handle_4xx_error)
app.register_error_handler(424, handle_4xx_error)
app.register_error_handler(429, handle_4xx_error)
app.register_error_handler(431, handle_4xx_error)
app.register_error_handler(451, handle_4xx_error)


app.register_error_handler(500, handle_5xx_error)
app.register_error_handler(501, handle_5xx_error)
app.register_error_handler(502, handle_5xx_error)
app.register_error_handler(503, handle_5xx_error)
app.register_error_handler(504, handle_5xx_error)
app.register_error_handler(505, handle_5xx_error)

emotion_dict = {
    0: "Angry 😡",
    1: "Disgust 🤢",
    2: "Fear 😨",
    3: "Happy 🙂",
    4: "Sad 😢",
    5: "Surprise 😮",
    6: "Neutral 😐",
}

json_file = open("model.json", "r")
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

model.load_weights("model_weights.h5")

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


@app.route("/detect-face", methods=["POST"])
def detect_face():
    id = 1

    image_data = request.json["image_data"]
    image_data = base64.b64decode(image_data.split(",")[1])

    nparr = np.frombuffer(image_data, np.uint8)

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(image=gray, scaleFactor=1.3, minNeighbors=4)

    response = {"faces": []}

    for x, y, w, h in faces:
        cv2.rectangle(
            img=img, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2
        )
        roi_gray = gray[y : y + h, x : x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            prediction = model.predict(roi)[0]
            maxindex = int(np.argmax(prediction))
            emotion = emotion_dict[maxindex]
            emotion = emotion[:-2]

        percentage = float(prediction[maxindex] * 100)
        percentage = round(percentage, 2)

        face_info = {
            "id": str(id),
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "emotion": emotion,
            "percentage": str(percentage),
        }

        face_info["x"] = json.dumps(face_info["x"].tolist())
        face_info["y"] = json.dumps(face_info["y"].tolist())
        face_info["width"] = json.dumps(face_info["width"].tolist())
        face_info["height"] = json.dumps(face_info["height"].tolist())

        response["faces"].append(face_info)
        id += 1

    return jsonify(response)


@app.route("/image", methods=["GET"])
def image():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]
    return render_template("image.html", options=options)


def nl_to_br_filter(s):
    return s.replace("\n", "<br>")


app.jinja_env.filters["nl_to_br"] = nl_to_br_filter


def get_url_content(image_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(image_url, headers=headers)
    response.raise_for_status()

    return response.content


@app.route("/classified-image", methods=["POST"])
def image_classify():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    file = request.files["image-file"]

    if file:
        image_data = file.read()
    else:
        try:
            image_url = request.form["image-url"]
            image_data = get_url_content(image_url)
        except (requests.exceptions.RequestException, IOError):
            error_message = "\nReasons:\n1) URL is not valid!\n2) URL does not point to an image!\
            \n3) URL does not end with an image file extension such as: .jpg, .jpeg, and .png!\
            \n4) Due to security settings of the website hosting the provided image, the image \
            cannot be accessed!\nPlease save it and then upload it!"
            return render_template("error.html", options=options, error=error_message)
    try:
        image_array = np.frombuffer(image_data, np.uint8)

        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            image=gray_img, scaleFactor=1.3, minNeighbors=4
        )

        id = 1
        emotions = []

        if len(faces) == 0:
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], "classified-image.png")
            cv2.imwrite(img_path, img)
            return render_template(
                "classified-image.html", options=options, emotions=emotions
            )

        for x, y, w, h in faces:
            cv2.rectangle(
                img=img,
                pt1=(x, y),
                pt2=(x + w, y + h),
                color=(0, 255, 255),
                thickness=2,
            )
            roi_gray = gray_img[y : y + h, x : x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype("float") / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                prediction = model.predict(roi)[0]
                maxindex = int(np.argmax(prediction))
                emotion = emotion_dict[maxindex]
                emotion_emoji = emotion[-1]
                emotion = emotion[:-2]
                emotions.append((id, emotion, emotion_emoji))

            label_position = (x, y)
            message = f"Person {id}: {emotion} ({prediction[maxindex] * 100:.2f}%)"

            cv2.putText(
                img=img,
                text=message,
                org=label_position,
                fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                fontScale=0.9,
                color=(0, 0, 255),
                thickness=2,
            )
            id += 1
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], "classified-image.png")
            cv2.imwrite(img_path, img)
    except:
        error_message = "Unable to process the image! Please check the image!"
        return render_template("error.html", options=options, error=error_message)

    return render_template("classified-image.html", options=options, emotions=emotions)


@app.route("/group-real-time-video", methods=["GET"])
def group_real_time_video():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    return render_template("group_real_time_video.html", options=options)


@app.route("/single-person-acting-practice", methods=["GET"])
def single_person_acting_practice():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    return render_template("single_person_acting_practice.html", options=options)


@app.route("/process-captured-image", methods=["POST"])
def process_captured_image():
    image_data = request.json["image_data"]
    image_data = base64.b64decode(image_data.split(",")[1])

    nparr = np.frombuffer(image_data, np.uint8)

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        image=gray_img, scaleFactor=1.3, minNeighbors=4
    )

    id = 1
    emotions = []

    for x, y, w, h in faces:
        cv2.rectangle(
            img=img, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 255), thickness=1
        )
        roi_gray = gray_img[y : y + h, x : x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            prediction = model.predict(roi)[0]
            maxindex = int(np.argmax(prediction))
            emotion = emotion_dict[maxindex]
            emotion_emoji = emotion[-1]
            emotion = emotion[:-2]
            emotions.append((id, emotion, emotion_emoji))

        label_position = (x, y)
        message = f"Person {id}: {emotion} ({prediction[maxindex] * 100:.2f}%)"
        cv2.putText(
            img=img,
            text=message,
            org=label_position,
            fontFace=cv2.FONT_HERSHEY_TRIPLEX,
            fontScale=0.3,
            color=(0, 0, 255),
            thickness=1,
        )
        id += 1
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], "classified-image.png")
        cv2.imwrite(img_path, img)

    buffer = BytesIO()
    is_success, buffer_arr = cv2.imencode(".png", img)
    buffer.write(buffer_arr.tobytes())

    arr_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({"processed_image_data": f"data:image/png;base64,{arr_b64}"})


@app.route("/single-person-real-time-video", methods=["GET"])
def single_person_real_time_video():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    return render_template("single_person_real_time_video.html", options=options)


@app.route("/detect-face-chart", methods=["POST"])
def detect_face_chart():
    if "emotion_count" not in session:
        session["emotion_count"] = 0
    if "angry_count" not in session:
        session["angry_count"] = 0
    if "disgust_count" not in session:
        session["disgust_count"] = 0
    if "fear_count" not in session:
        session["fear_count"] = 0
    if "happy_count" not in session:
        session["happy_count"] = 0
    if "sad_count" not in session:
        session["sad_count"] = 0
    if "surprise_count" not in session:
        session["surprise_count"] = 0
    if "neutral_count" not in session:
        session["neutral_count"] = 0

    try:
        image_data = request.json["image_data"]
        image_data = base64.b64decode(image_data.split(",")[1])

        nparr = np.frombuffer(image_data, np.uint8)

        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            image=gray, scaleFactor=1.3, minNeighbors=4
        )

        response = {"faces": []}

        for x, y, w, h in faces:
            cv2.rectangle(
                img=img, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2
            )
            roi_gray = gray[y : y + h, x : x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype("float") / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                prediction = model.predict(roi)[0]
                maxindex = int(np.argmax(prediction))
                emotion = emotion_dict[maxindex]
                emotion = emotion[:-2]

                session["emotion_count"] += 1

                if emotion == "Angry":
                    session["angry_count"] += 1
                elif emotion == "Disgust":
                    session["disgust_count"] += 1
                elif emotion == "Fear":
                    session["fear_count"] += 1
                elif emotion == "Happy":
                    session["happy_count"] += 1
                elif emotion == "Sad":
                    session["sad_count"] += 1
                elif emotion == "Surprise":
                    session["surprise_count"] += 1
                elif emotion == "Neutral":
                    session["neutral_count"] += 1

            percentage = float(prediction[maxindex] * 100)
            percentage = round(percentage, 2)

            face_info = {
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "emotion": emotion,
                "percentage": percentage,
            }

            face_info["x"] = json.dumps(face_info["x"].tolist())
            face_info["y"] = json.dumps(face_info["y"].tolist())
            face_info["width"] = json.dumps(face_info["width"].tolist())
            face_info["height"] = json.dumps(face_info["height"].tolist())

            response["faces"].append(face_info)
        return jsonify(response)
    except:
        error_message = "Unable to process the image! Please check the image!"
        return render_template("error.html", options=options, error=error_message)


@app.route("/charts", methods=["GET"])
def charts():
    if "emotion_count" not in session:
        session["emotion_count"] = 0
    if "angry_count" not in session:
        session["angry_count"] = 0
    if "disgust_count" not in session:
        session["disgust_count"] = 0
    if "fear_count" not in session:
        session["fear_count"] = 0
    if "happy_count" not in session:
        session["happy_count"] = 0
    if "sad_count" not in session:
        session["sad_count"] = 0
    if "surprise_count" not in session:
        session["surprise_count"] = 0
    if "neutral_count" not in session:
        session["neutral_count"] = 0

    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    return render_template(
        "charts.html",
        options=options,
        emotion_count=session["emotion_count"],
        angry_count=session["angry_count"],
        disgust_count=session["disgust_count"],
        fear_count=session["fear_count"],
        happy_count=session["happy_count"],
        sad_count=session["sad_count"],
        surprise_count=session["surprise_count"],
        neutral_count=session["neutral_count"],
    )


@app.route("/emotion-counts", methods=["GET"])
def emotion_counts():
    if "emotion_count" not in session:
        session["emotion_count"] = 0
    if "angry_count" not in session:
        session["angry_count"] = 0
    if "disgust_count" not in session:
        session["disgust_count"] = 0
    if "fear_count" not in session:
        session["fear_count"] = 0
    if "happy_count" not in session:
        session["happy_count"] = 0
    if "sad_count" not in session:
        session["sad_count"] = 0
    if "surprise_count" not in session:
        session["surprise_count"] = 0
    if "neutral_count" not in session:
        session["neutral_count"] = 0

    counts = {
        "angry_count": session["angry_count"],
        "disgust_count": session["disgust_count"],
        "fear_count": session["fear_count"],
        "happy_count": session["happy_count"],
        "sad_count": session["sad_count"],
        "surprise_count": session["surprise_count"],
        "neutral_count": session["neutral_count"],
    }

    return jsonify(counts)


@app.route("/reset-counts", methods=["POST"])
def reset_counts():
    if "emotion_count" not in session:
        session["emotion_count"] = 0
    if "angry_count" not in session:
        session["angry_count"] = 0
    if "disgust_count" not in session:
        session["disgust_count"] = 0
    if "fear_count" not in session:
        session["fear_count"] = 0
    if "happy_count" not in session:
        session["happy_count"] = 0
    if "sad_count" not in session:
        session["sad_count"] = 0
    if "surprise_count" not in session:
        session["surprise_count"] = 0
    if "neutral_count" not in session:
        session["neutral_count"] = 0

    session["emotion_count"] = 0
    session["angry_count"] = 0
    session["disgust_count"] = 0
    session["fear_count"] = 0
    session["happy_count"] = 0
    session["sad_count"] = 0
    session["surprise_count"] = 0
    session["neutral_count"] = 0

    counts = {
        "emotion_count": session["emotion_count"],
        "angry_count": session["angry_count"],
        "disgust_count": session["disgust_count"],
        "fear_count": session["fear_count"],
        "happy_count": session["happy_count"],
        "sad_count": session["sad_count"],
        "surprise_count": session["surprise_count"],
        "neutral_count": session["neutral_count"],
    }

    return jsonify(counts)


@app.route("/charts-side", methods=["GET"])
def charts_side():
    if "emotion_count" not in session:
        session["emotion_count"] = 0
    if "angry_count" not in session:
        session["angry_count"] = 0
    if "disgust_count" not in session:
        session["disgust_count"] = 0
    if "fear_count" not in session:
        session["fear_count"] = 0
    if "happy_count" not in session:
        session["happy_count"] = 0
    if "sad_count" not in session:
        session["sad_count"] = 0
    if "surprise_count" not in session:
        session["surprise_count"] = 0
    if "neutral_count" not in session:
        session["neutral_count"] = 0

    return render_template(
        "charts_side.html",
        emotion_count=session["emotion_count"],
        angry_count=session["angry_count"],
        disgust_count=session["disgust_count"],
        fear_count=session["fear_count"],
        happy_count=session["happy_count"],
        sad_count=session["sad_count"],
        surprise_count=session["surprise_count"],
        neutral_count=session["neutral_count"],
    )


@app.route("/")
def index():
    options = [
        "Home",
        "Image",
        "Group Real Time Video",
        "Single Person Acting Practice",
        "Single Person Real Time Video",
        "Charts",
    ]

    return render_template("index.html", options=options)


if __name__ == "__main__":
    app.run(debug=False)
