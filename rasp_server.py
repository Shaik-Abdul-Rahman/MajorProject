from flask import Flask, Response
from picamera import PiCamera
import time
import io
import requests

app = Flask(__name__)

# Initialize PiCamera
camera = PiCamera()
camera.resolution = (640, 480)  # Set resolution as needed

# Define a generator function to capture frames from PiCamera
def generate_frames():
    # Allow camera to warm up
    time.sleep(2)
    
    while True:
        # Create a byte stream to store image data
        stream = io.BytesIO()
        
        # Capture frame from PiCamera and save it to stream
        camera.capture(stream, format='jpeg', use_video_port=True)
        
        # Rewind the stream to the beginning so it can be read
        stream.seek(0)
        
        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')
        
        # Sleep for a short interval to control frame rate (adjust as needed)
        time.sleep(0.1)

# Define route for camera feed
@app.route('/camera_feed')
def camera_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
