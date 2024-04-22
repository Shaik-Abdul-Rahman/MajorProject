from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect('/home')
    return render_template('signup.html')

appliance_status = 'OFF'

# Route for the home page
@app.route('/home',methods =['GET', 'POST'])
def home():

    if 'username' in session:
        return render_template('home.html', status=appliance_status)
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

if __name__ == '__main__':
    app.run(debug=True)
