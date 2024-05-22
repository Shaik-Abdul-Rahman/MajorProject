from flask import Flask, render_template, request, redirect, session, jsonify, Response
import os
import random
import time
import cv2
from mysql import connector
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)
current_temperature = 100
URL = 'https://lionfish-intent-nicely.ngrok-free.app'

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
        app5 INT DEFAULT 0,
        active INT DEFAULT 0,
        temp DECIMAL(10,2) DEFAULT 27.50,
        humidity DECIMAL DEFAULT 30.50,
        rfid INT DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def active_status(active=True):
    conn = get_db_connection()
    cursor = conn.cursor()

    active = 1 if active == True else 0
    if active:
        cursor.execute('UPDATE users SET active = IF(username = %s ,1,0)',(session['username'],))
    else:
        cursor.execute('UPDATE users SET active = %s',(0,))
    conn.commit()
    conn.close()
        
def user_signup(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s',(username,))
    user = cursor.fetchall()
    if user:
        conn.close()
        return True
    else:
        cursor.execute('INSERT INTO users (username, password, active) VALUES (%s, %s, %s)',(username, password, 1))
        conn.commit()
        conn.close()
        return False


def temp_update():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT temp,humidity FROM users WHERE username = %s',(session['username'],))
    user = cursor.fetchone()
    conn.close()
    print(user)
    return user
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
            session['password'] = password
            active_status()
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
        user_exists = user_signup(username,password)
        if user_exists:
            return render_template('signup.html', error='The username already exists')
        session['username'] = username
        session['password'] = password
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
    active_status(active=False)
    time.sleep(3)
    session.pop('username', None)
    return redirect('/')

@app.route('/')
def index():
    return redirect('/login')

@app.route('/get_temperature')
def get_temperature():
    global current_temperature 
    data = temp_update()
    return jsonify({'temperature': data[0], 'humidity': data[1]})

@app.route('/update_status_and_temperature', methods=['POST'])
def update_status_and_temperature():
    data = request.get_json()
    status = data.get('status')
    appliance = data.get('applianceNumber')
    update_column(session['username'], status, appliance)
    return jsonify({'status': status})

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
    response = requests.get('https://lionfish-intent-nicely.ngrok-free.app/camera_feed')

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the camera feed content from the response
        camera_feed = response.content
        
        # Return the camera feed content with the appropriate mimetype
        return Response(camera_feed, mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        # Return an error message if the request was not successful
        return 'Error: Unable to fetch camera feed from the external server'
    
@app.route('/rfid_register')
def rfid_register():
    return render_template('rfid_register.html')

@app.route('/detail_confirmation',methods=['POST'])
def detail_confirmation():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = %s and password = %s',(username,password))
    user = cursor.fetchone()
    #data = {'username': username, 'password': password}
    # try:

    #     response = requests.post(URL,json=data)

    #     if response.status_code == 200:
    if user:
        return jsonify({'confirmation': 'success'})
    else:
        return jsonify({'confirmation': 'failure'})

    

@app.route('/confirm_card_registration',methods = ['GET'])
def card_confirmation():
    detail = {'username':session['username'],'password':session['password']}
    
        
    response = requests.post(URL+'/card_registration',json=detail)
    if response.status_code == 200:
        data = response.json()
        reg = data.get('registration')
        id = data.get('id')
        print_data(id)

        time.sleep(5)
        if id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET rfid = %s WHERE username = %s',(id,session['username']))
            conn.commit()
            conn.close()
            return jsonify({'registration':"success"})
        
        else:
            return jsonify({'registration':"failure"})

def print_data(data):
    print(data)

    time.sleep(5)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
