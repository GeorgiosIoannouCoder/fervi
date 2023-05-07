var video = document.getElementById('video-acting');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
        var video = document.getElementById('video-acting');
        video.srcObject = stream;
        video.play();
    })
    .catch(function (error) {
        console.log('Error accessing camera:', error);
    });

var canvas = document.getElementById('canvas-acting');
var context = canvas.getContext('2d');

document.getElementById('btn-capture').addEventListener('click', function () {
    updateEmotion();

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    var dataUrl = canvas.toDataURL('image/jpeg');
    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/process-captured-image', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onload = function () {
        if (this.status === 200) {
            var response = JSON.parse(this.responseText);
            var processedImageData = response.processed_image_data;
            document.getElementById('processed-image').src = processedImageData;
        } else {
            console.log('Error processing image:', this.status, this.statusText);
        }
    };
    xhr.send(JSON.stringify({ image_data: dataUrl }));
});

var emotions = ["Angry 😡", "Disgust 🤢", "Fear 😨", "Happy 🙂", "Sad 😢", "Surprise 😮", "Neutral 😐"]

function updateEmotion() {
    var randomIndex = Math.floor(Math.random() * emotions.length);
    var newEmotion = emotions[randomIndex];

    document.getElementById('emotion').innerText = newEmotion;
}

updateEmotion();