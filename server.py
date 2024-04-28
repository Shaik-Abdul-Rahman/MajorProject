from flask import Flask, render_template, request, redirect, session, jsonify, Response
import os
import random
import time
import cv2
from mysql import connector

app = Flask(__name__)
app.secret_key = os.urandom(24)
current_temperature = 100


def init_status(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    #print(user)
    cursor.execute('SELECT * FROM users WHERE username = %s',(user,))
    data = cursor.fetchone()
    #print(data)
    status = data[3:]
    print(status)
    #print('hello')
    conn.close()
    #print(status1)
    return status


def update_column(username, status,app):
    conn = get_db_connection()
    status = 1 if status == 'ON' else 0
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET app{app} = %s  WHERE username = %s ',(status ,username))
    conn.commit()
    conn.close()


# Function to create a database connection
def get_db_connection():
    conn = connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )
    return conn

# Function to create the user table in the database
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        app1 INT DEFAULT 0,
        app2 INT DEFAULT 0,
        app3 INT DEFAULT 0,
        app4 INT DEFAULT 0,
        app5 INT DEFAULT 0
    )''')
    conn.commit()
    conn.close()

create_table()

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/home')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = %s', (username,))
        user_exists = cursor.fetchone()
        if user_exists:
            return render_template('signup.html', error='The username already exists')
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect('/home')
    return render_template('signup.html')

# Route for the home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        appliance_status = init_status(session['username'])
        appliance_status = ['ON' if stat == 1 else 'OFF' for stat in appliance_status]
        return render_template('home.html', status1=appliance_status[0], status2=appliance_status[1],
                               status3=appliance_status[2], status4=appliance_status[3], status5=appliance_status[4])
    else:
        return 'You are not logged in. <a href="/login">Login</a> or <a href="/signup">Sign up</a>.'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/')
def index():
    return redirect('/login')

@app.route('/get_temperature')
def get_temperature():
    global current_temperature 
    current_temperature += random.uniform(-1, 1)
    time.sleep(1)  # Simulate delay
    return jsonify({'temperature': current_temperature, 'humidity': current_temperature})

@app.route('/update_status_and_temperature', methods=['POST'])
def update_status_and_temperature():
    data = request.get_json()
    status = data.get('status')
    appliance = data.get('applianceNumber')
    update_column(session['username'], status, appliance)
    return jsonify({'status': status, 'temperature': current_temperature, 'humidity': current_temperature})

def generate_frames():
    camera = cv2.VideoCapture(1)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/get_camera_feed')
def get_camera_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
