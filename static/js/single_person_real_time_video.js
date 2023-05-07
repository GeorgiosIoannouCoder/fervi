const video = document.getElementById('video-chart');
const canvas = document.getElementById('canvas');
const canvasContainer = document.getElementById('canvas-container');
const context = canvas.getContext('2d');

function sendFrame() {
    context.drawImage(video, 0, 0, 640, 480);
    const imageData = canvas.toDataURL('image/jpeg');

    fetch('/detect-face-chart', {
        body: JSON.stringify({ image_data: imageData }),
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            context.clearRect(0, 0, canvas.width, canvas.height);
            context.drawImage(video, 0, 0, 640, 480);
            for (const face of data.faces) {
                context.beginPath();
                context.rect(face.x, face.y, face.width, face.height);
                context.strokeStyle = '#ffff00';
                context.lineWidth = 1.5;
                context.stroke();
                context.font = '1.3rem monospace';
                context.fillStyle = '#ff0000';
                context.fillText(`Emotion: ${face.emotion} (${face.percentage}%)`, face.x, face.y);
            }
        });
}

setInterval(sendFrame, 500);

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.play();
    });

function resetCounts() {
    fetch('/reset-counts', {
        method: 'POST'
    })
        .then(response => response.json());
}

function resizeCanvas() {
    const aspectRatio = canvas.width / canvas.height;
    const containerWidth = canvasContainer.clientWidth;
    const newCanvasWidth = containerWidth;
    const newCanvasHeight = containerWidth / aspectRatio;

    canvas.style.width = newCanvasWidth + 'px';
    canvas.style.height = newCanvasHeight + 'px';
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();