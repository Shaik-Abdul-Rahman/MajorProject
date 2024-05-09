import threading
import time
import RPi.GPIO as GPIO
#from sensors import *

from sensorscgpt import *
from picamera import PiCamera
#import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
#import RPi.GPIO as gpio
from mysql import connector
#import threading

# Global variable for shared data
data = {}
def get_db_connection():
    conn = connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )
    return conn

def capture_img():
    with PiCamera() as camera:
        camera.resolution = (320, 320)
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
    msg['Subject'] = 'Intrusion detected'
    message = f'CLICK ON THIS LINK TO SEE THE LIVE FEED/n{URL}/camera_feed'

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
    print('Mail sent.')



def intrusion_detect():
    try:
        while True:
            time.sleep(2)
            usensor = UltraSensor()
            dist = usensor.update_distance()
            print(dist)
            if dist is not None and dist < 0.5:
                print('Intrusion detected, starting countdown...')
                time.sleep(5)
                dist = usensor.update_distance()
                if dist is not None and dist < 0.9:
                    capture = capture_img()
                    if capture:
                        email_conn()
            else:
                print('No person detected')
    except Exception as e:
        print(f'Error in intrusion_detect: {e}')

def app_update():
    global data
    print('Starting app update...')
    while True:
        time.sleep(5)
        if 'id' in data:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Implement database update code here
                cursor.execute('SELECT * FROM users WHERE rfid = %s',(data['id'],))
                status = cursor.fetchone()
                #details = status[3:8]
                bulb_ = Bulb(status[3:8])
                temp_sensor = DhtSensor()
                temp_readings = temp_sensor.update_readings()
                print(temp_readings)
                cursor.execute('UPDATE users SET temp = %s, humidity = %s WHERE rfid = %s',(temp_readings['temperature'],temp_readings['humidity'],data['id']))
                conn.commit()
                    
            except Exception as e:
                print(f'Database error in app_update: {e}')
            finally:
                conn.close()
        else:
            print('Waiting for user to enter.')

def button_pressed(channel):
    print('Button pressed.')
    rfid_ = RFID()
    global data
    data = rfid_.read()
    print(data)
    print(data.get('username'))
    if 'id' in data:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Implement database query code
            cursor.execute('SELECT * FROM users WHERE rfid = %s',(data['id'],))
            status = cursor.fetchone()
            #conn.close()
            #details = status[3:8]
            if status:
                print(status)
                bulb_ = Bulb(status[3:8])
                earlier_status = bulb_.change_status()
                print('Unlocked' if earlier_status == GPIO.LOW else 'Locked')
            else:
                print('Unregisterd User')
            
        except Exception as e:
            print(f'Database error in button_pressed: {e}')
        finally:
            conn.close()
    else:
        print('No RFID data found.')

def init_rfid():
    BUTTON_PIN = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=200)
        print('Waiting for RFID...')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

def main():
    thread1 = threading.Thread(target=init_rfid)
    thread2 = threading.Thread(target=intrusion_detect)
    thread3 = threading.Thread(target=app_update)

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    print('All functions completed.')

if __name__ == '__main__':
    main()