from flask import Flask, render_template, request, redirect, session, jsonify, Response
import sqlite3
import os
import random
import time
import cv2

app = Flask(__name__)
app.secret_key = os.urandom(24)


def init_status(user):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    print(user)
    cursor.execute('SELECT * FROM users WHERE username = ?',(user,))
    data = cursor.fetchone()
    print(data)
    status1 = data[3]
    print('hello')
    
    print(status1)
    return status1



# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the user table in the database
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 username TEXT NOT NULL, password TEXT NOT NULL,
                 app1 INTEGER DEFAULT 0,app2 INTEGER DEFAULT 0,app3 INTEGER DEFAULT 0)''')
    conn.close()

create_table()

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
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
        cursor.execute('SELECT username FROM users WHERE username = ?',(username,))
        user_exists = cursor.fetchone()
        if user_exists:
            print(user_exists)
            return render_template('signup.html',error = 'The username already exists')
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect('/home')
    return render_template('signup.html')


# Route for the home page
@app.route('/home',methods =['GET', 'POST'])
def home():

    if 'username' in session:
        appliance_status = init_status(session['username'])
        if appliance_status == 1:
            appliance_status = 'ON'
        else:
            appliance_status  = 'OFF'
        return render_template('home.html', status=appliance_status,temp=appliance_status)
    else:
        return 'You are not logged in. <a href="/login">Login</a> or <a href="/signup">Sign up</a>.'

    
# Route to logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# Route to update status
@app.route('/update_status',methods=['POST'])
def update_status():
    print("Received request to update status")  # Print statement to check if the route is being accessed
    global appliance_status
    data = request.get_json()
    status = data['status']
    appliance_status = status
    print(session['username'])
    update_column(session['username'],appliance_status)
    print("Appliance Status:", appliance_status)  # Print the appliance status to console
    return jsonify({'message': 'Status updated successfully', 'status': appliance_status})


def update_column(username, status):
    conn = sqlite3.connect('database.db')
    if status == 'ON':
        status = 1
    else :
        status = 0
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET app1 = ? WHERE username = ? ',(status, username))
    conn.commit()
    conn.close()


current_temperature = 100
@app.route('/get_temperature')
def get_temperature():
    global current_temperature  # Access the global temperature variable
    # Simulate temperature changes (for demonstration purposes)
    current_temperature += random.uniform(-1, 1)
    time.sleep(1)  # Simulate delay
    return jsonify(current_temperature)



@app.route('/update_status_and_temperature', methods=['POST'])
def update_status_and_temperature():
    global appliance_status, current_temperature  # Access the global status and temperature variables
    data = request.get_json()
    status = data['status']
    update_column(session['username'],status)
    # Simulate temperature changes (for demonstration purposes)
    current_temperature += random.uniform(-1, 1)
    
    # Update the status and temperature data
    appliance_status = status
    
    return jsonify({'status': appliance_status, 'temperature': current_temperature})




def generate_frames():
    camera = cv2.VideoCapture(1)  # Change the argument to the camera index if using multiple cameras

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to serve the camera feed
@app.route('/get_camera_feed')
def get_camera_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    app.run(debug=True)
