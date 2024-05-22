import logging
import threading
import time
from mfrc522 import SimpleMFRC522
from mysql import connector
from picamera import PiCamera
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import RPi.GPIO as gpio
from sensors import Appliances, UltraSensor, DhtSensor

# Configure logging for each thread
def setup_logging(log_file):
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

# Global loggers for each thread
rfid_logger = setup_logging('rfid.log')
motion_logger = setup_logging('motion.log')
update_logger = setup_logging('update.log')

def capture_img():
    try:
        with PiCamera() as camera:
            camera.resolution = (320, 320)
            time.sleep(4)
            camera.capture('intrusion.jpg')
        motion_logger.info('Image captured successfully.')
        return True
    except Exception as e:
        motion_logger.error(f'Error capturing image: {e}')
        return False

def email_conn():
    try:
        sender_email = "mohammad.ahmed1774@gmail.com"
        receiver_email = "mohammad.ahmed1774@gmail.com"
        password = "kehx negx kqvn luhw"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'intrusion detected'
        message = 'CLICK ON THIS LINK TO SEE THE LIVE FEED/n{URL}+/camera_feed'

        msg.attach(MIMEText(message, 'plain'))

        with open('intrusion.jpg', 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data, name='intrusion.jpg')
            msg.attach(image)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        motion_logger.info('Email sent')
    except Exception as e:
        motion_logger.error(f'Error sending email: {e}')

def motion_sensor():
    distance_sensor = UltraSensor()
    try:
        while True:
            time.sleep(5)
            dist = distance_sensor.update_dist()
            motion_logger.info(f'Distance: {dist}')
            if dist < 0.5:
                motion_logger.info('Intrusion timer starts')
                time.sleep(5)
                dist = distance_sensor.update_dist()
                if dist < 0.5:
                    motion_logger.info('Intrusion detected')
                    capture = capture_img()
                    if capture:
                        email_conn()
                        time.sleep(30)
            else:
                motion_logger.info('No intrusion detected')
                time.sleep(5)
    except Exception as e:
        motion_logger.error(f'Error in motion sensor: {e}')
        distance_sensor.cleanup()
    except KeyboardInterrupt:
        motion_logger.info('KeyboardInterrupt')
        distance_sensor.cleanup()

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
button_pin = 21
rfid_pins = [8, 10, 9, 11, 22]
wait_for_button = True
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

def initialize_reader():
    return SimpleMFRC522()

data = {}
def read_rfid(reader):
    global data
    try:
        rfid_logger.info('Place your card')
        id, text = reader.read()
        data['id'] = id
        data['username'] = text
        rfid_logger.info(f'Card ID: {id}, Text: {text}')
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
            rfid_logger.info(f'Status: {status}')
            bulb_ = Appliances(status[3:8])
            rfid_logger.info('Unlocked')
        else:
            rfid_logger.warning('Unregistered User')
        
    except Exception as e:
        rfid_logger.error(f'Error reading RFID card: {e}')
    finally:
        gpio.cleanup(rfid_pins)
        rfid_logger.info('GPIO cleaned up')

def button_press(channel):
    global wait_for_button, reader
    if wait_for_button:
        wait_for_button = False
        read_rfid(reader)
        wait_for_button = True
        reader = initialize_reader()

def rfid_thread():
    global reader
    reader = initialize_reader()
    rfid_logger.info('Waiting for button press...')
    gpio.add_event_detect(button_pin, gpio.RISING, callback=button_press, bouncetime=200)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup(button_pin)
        gpio.cleanup(rfid_pins)
        rfid_logger.info('Cleaned up GPIO pins')

def update_app():
    global data
    temp_sensor = DhtSensor()
    try:
        while True:
            values = temp_sensor.update_readings()
            if 'id' in data:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE rfid = %s', (data['id'],))
                values_of_bulbs = cursor.fetchone()
                cursor.execute('UPDATE users SET temp = %s , humidity = %s', (values['temperature'], values['humidity']))
                conn.commit()
                conn.close()
                if values_of_bulbs:
                    update_logger.info(f'Values of bulbs: {values_of_bulbs}')
                    bulb_ = Appliances(values_of_bulbs[3:8])
                    update_logger.info('Unlocked')
                else:
                    update_logger.warning('Unregistered User')
                update_logger.info('Updated the bulbs')
                time.sleep(1)
            else:
                update_logger.info('Wait for user to enter')
                time.sleep(5)
    except Exception as e:
        update_logger.error(f'Error in temperature sensing and update: {e}')
        temp_sensor.cleanup()

if __name__ == '__main__':
    rfid = threading.Thread(target=rfid_thread)
    intrusion = threading.Thread(target=motion_sensor)
    update_read = threading.Thread(target=update_app)
    
    rfid.start()
    intrusion.start()
    update_read.start()
    
    rfid.join()
    intrusion.join()
    update_read.join()
    rfid_logger.info('RFID thread stopped')
