from sensors import Appliances
import threading
import RPi.GPIO as gpio
import time
from mfrc522 import SimpleMFRC522
from mysql import connector

gpio.setwarnings(False)
# Set up GPIO mode
gpio.setmode(gpio.BCM)

# Define global variables
button_pin = 21
rfid_pins = [8, 10, 9, 11, 22]
wait_for_button = True  # Flag to control waiting for button press

# Set up button pin
gpio.setup(button_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)




def get_db_connection():
    conn = connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )
    return conn
# Function to initialize RFID reader
def initialize_reader():
    return SimpleMFRC522()

# Function to read RFID card
def read_rfid(reader):
    data = {}
    try:
        print('Place your card')
        id, text = reader.read()
        data['id'] = id
        data['username'] = text
        print(id, text)
        # Further processing based on RFID data
        conn = get_db_connection()
        cursor = conn.cursor()
        status = 0
        cursor.execute('UPDATE users SET app5 = %s WHERE rfid = %s', (status, id))
        conn.commit()
        conn.close()
        
        time.sleep(1)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE rfid = %s', (id,))
        status = cursor.fetchone()
        conn.close()
        
        if status:
            print(status)
            bulb_ = Appliances(status[3:8])
            print('Unlocked')
        else:
            print('Unregistered User')
        
    except Exception as e:
        print(f'Error reading RFID card: {e}')
    finally:
        gpio.cleanup(rfid_pins)
        print('gpio cleaned up')

# Function to handle button press event
def button_press(channel):
    global wait_for_button,reader
    if wait_for_button:
        wait_for_button = False  # Allow RFID reading
        read_rfid(reader)
        wait_for_button = True
        reader = initialize_reader()
        # Wait for the next button press

# RFID thread function
def rfid_thread():
    global reader
    reader = initialize_reader()
    print('Waiting for button press...')
    gpio.add_event_detect(button_pin, gpio.RISING, callback=button_press, bouncetime=200)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup(button_pin)
        gpio.cleanup(rfid_pins)
        print('Cleaned up GPIO pins')

if __name__ == '__main__':
    rfid = threading.Thread(target=rfid_thread)
    rfid.start()
    rfid.join()
    print('RFID thread stopped')
