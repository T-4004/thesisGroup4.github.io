// Function to start the webcam
function startWebcam() {
    // Access the video element
    let video = document.getElementById('videoFeed');

    // Use navigator.mediaDevices.getUserMedia to start the webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            // Set the video source to the webcam stream
            video.srcObject = stream;
        })
        .catch(function (error) {
            console.log('Error starting webcam: ', error);
        });
}

// Function to capture an image
function captureImage() {
    // Access the video element
    let video = document.getElementById('videoFeed');

    // Create a canvas element to draw the captured frame
    let canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current frame of the video onto the canvas
    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get the base64 data URL of the captured image
    let imageData = canvas.toDataURL('image/jpeg');

    // Send the captured image data to the server (you can use AJAX or fetch)
    // For simplicity, let's just log the image data to the console
    console.log(imageData);

    // Call the analyzeImage function with the captured image data
    analyzeImage(imageData);
}

// Function to analyze the captured image
function analyzeImage(imageData) {
    // Send the captured image data to the server for analysis (you can use AJAX or fetch)
    // For simplicity, let's just log a message to the console
    console.log('Analyzing image:', imageData);
}

// Event listener for when the DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Access the start webcam button
    const startWebcamButton = document.getElementById('startWebcamButton');

    // Add event listener to start webcam button
    startWebcamButton.addEventListener('click', startWebcam);

    // Access the capture image button
    const captureImageButton = document.getElementById('captureImageButton');

    // Add event listener to capture image button
    captureImageButton.addEventListener('click', captureImage);
});
