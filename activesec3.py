from sensors import Appliances, UltraSensor, DhtSensor
import threading
import RPi.GPIO as gpio
import time
from mfrc522 import SimpleMFRC522
from mysql import connector
from picamera import PiCamera
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os







def capture_img():
    
    with PiCamera() as camera:
        camera.resolution=(320,320)
        time.sleep(4)
        camera.capture('intrusion.jpg')


    print('Image captured successfully.')
    return True 
   

def email_conn():
    sender_email = "mohammad.ahmed1774@gmail.com"
    receiver_email = "mohammad.ahmed1774@gmail.com"
    password = "kehx negx kqvn luhw"

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'intrusion detected'
    message = 'CLICK ON THIS LINK TO SEE THE LIVE FEED/n{URL}+/camera_feed'

    # Attach message
    msg.attach(MIMEText(message, 'plain'))

    with open('intrusion.jpg', 'rb') as f:
        img_data = f.read()
        image = MIMEImage(img_data, name='intrusion.jpg')
        msg.attach(image)

    # Connect to the SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print('mail sent')




def motion_sensor():
    
    distance_sensor = UltraSensor()
     
    try:
        while True:
            time.sleep(5)
            dist = distance_sensor.update_dist()
            print(dist)
            if dist < 0.5:
                print('intrusion  timer starts')
                
                time.sleep(5)
                dist = distance_sensor.update_dist()
                if dist < 0.5:
                    print('intrusion detected')
                    capture = capture_img()
                    if capture:
                        email_conn()
                        time.sleep(30)
            else:
                print('no intrusion detected')
                time.sleep(5)        
    except Exception as e:
        print('there has been an error', e)
        distance_sensor.cleanup()
        motion_sensor()
    except KeyboardInterrupt:
        print('KeyboardInterrup')
        distance_sensor.cleanup()










gpio.setwarnings(False)
# Set up GPIO mode
gpio.setmode(gpio.BCM)

# Define global variables
button_pin = 21
rfid_pins = [8, 10, 9, 11, 22]
wait_for_button = True  # Flag to control waiting for button press

# Set up button pin
gpio.setup(button_pin, gpio.IN, pull_up_down=gpio.PUD_UP)




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


data = {}
# Function to read RFID card
def read_rfid(reader):
    global data
    
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
            gpio.output(20, gpio.LOW)
            gpio.output(16, gpio.HIGH)
            gpio.output(5,gpio.LOW)
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
    
    red = 20
    green = 16
    logged = 5
    gpio.setup(logged, gpio.OUT)
    gpio.output(logged, gpio.HIGH)
    gpio.setup(red, gpio.OUT)
    gpio.setup(green, gpio.OUT)
    gpio.output(red, gpio.HIGH)
    gpio.output(green, gpio.LOW)
    
    reader = initialize_reader()
    print('Waiting for button press...')
    gpio.add_event_detect(button_pin, gpio.FALLING, callback=button_press, bouncetime=200)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup(button_pin)
        gpio.cleanup(rfid_pins)
        print('Cleaned up GPIO pins')
        
        





def update_app():
    global data
#    try:
    temp_sensor = DhtSensor()
    while True:
        
        values = temp_sensor.update_readings()
        if 'id' in data:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE rfid = %s',(data['id'],))
            values_of_bulbs = cursor.fetchone()
            
            cursor.execute('UPDATE users SET temp = %s , humidity = %s',(values['temperature'],values['humidity']))
            conn.commit()
            conn.close()
#                bulb_ = Appliances(values[3:8])
            if values_of_bulbs:
                print(values_of_bulbs)
                bulb_ = Appliances(values_of_bulbs[3:8])
                print('Unlocked')
            else:
                print('Unregistered User')
                print('updated the bulbs')
            time.sleep(1)
        else:
            print('wait for user to enter')
            time.sleep(5)
    #except Exception as e:
     #   print('error occured in temp sensing and update: ', e)
      #  temp_sensor.cleanup()
    
        
            






if __name__ == '__main__':
    rfid = threading.Thread(target=rfid_thread)
    intrusion = threading.Thread(target = motion_sensor)
    update_read = threading.Thread(target = update_app)
    
    rfid.start()
#    intrusion.start()
    update_read.start()
    
    rfid.join()
 #   intrusion.join()
    update_read.join()
    print('RFID thread stopped')
