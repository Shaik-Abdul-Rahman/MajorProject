from flask import Flask, Response,request,jsonify
from picamera import PiCamera
import time
import io
import requests
from mysql import connector
from sensors import *

app = Flask(__name__)

# Initialize PiCamera
camera = PiCamera()
camera.resolution = (640, 480)  # Set resolution as needed

def get_db_connection():
    conn = connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )
    return conn


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

@app.route('/card_registration',methods=['POST'])
def detail_confirmation():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    rfid_register = rfid()
    register = rfid_register.register(username)
    if register:
        cursor.execute('UPDATE users SET rfid = %s WHERE username = %s and password = %s',(register['id'],username,password))
        conn.commit()
        conn.close()
        return jsonify({'registration':'success','id':register['id']})
    else:
        return jsonify({'registration':'failure'})


    
    

if __name__ == '__main__':
    app.run(port=5000, debug=False)
