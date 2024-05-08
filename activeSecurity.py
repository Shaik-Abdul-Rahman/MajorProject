from sensors import *
from picamera import PiCamera
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import RPi.GPIO as gpio
from mysql import connector
import threading


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
    message = f'CLICK ON THIS LINK TO SEE THE LIVE FEED/n{URL}+/camera_feed'

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

def main():
    ultra_dist = UltraSensor()
    distance = ultra_dist.update_distance()
    
    while True:
        
        dist = ultra_dist.update_distance()
        try:
            #gpio.add_event_detect(BUTTON_PIN,gpio.FALLING, callback= button_pressed,bouncetime=200)
            if dist < 0.5:
                time.sleep(10)
                dist = ultra_dist.update_distance()
                if dist < 0.9:
                    capture = capture_img()
                    if capture:
                        email_conn()
        finally:
            gpio.cleanup()





def solenoid_check():
	BUTTON_PIN = 21
	gpio.setmode(gpio.BCM)
	gpio.setup(BUTTON_PIN,gpio.IN,pull_up_down = gpio.PUD_UP)
	gpio.add_event_detect(BUTTON_PIN,gpio.FALLING,callback = button_pressed,bouncetime = 200)
	try:
		print('watitin')
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass

	finally:
		gpio.cleanup()
            


def button_pressed(channel):
    print('button pressed')
    rfid_ = rfid()
    global data
    
    data = rfid_.read()
    print(data)
    print(data['username'])
    username = data['username']
    print(username)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s',(username,))
    status = cursor.fetchone()
    details = status[3:8]
    
    bulb_ = Bulb(details)
    bulb_.unlock_lock()
    conn.close()


def init_rfid():
    BUTTON_PIN = 21
    gpio.setmode(gpio.BCM)
    gpio.setup(BUTTON_PIN,gpio.IN,pull_up_down = gpio.PUD_UP)
    gpio.add_event_detect(BUTTON_PIN,gpio.FALLING,callback = button_pressed,bouncetime = 200)
    try:
        print('watitin')
        while True:
             time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
         gpio.cleanup()
    


def intrusion_detect():
    
    time.sleep(2)
   
    try:
        while True:
            usensor = UltraSensor()
            dist = usensor.update_distance()
            print(dist)
#            if dist < 0.5:
 #               time.sleep(10)
  #              dist = usensor.update_distance()
   #             if dist < 0.9:
    #                capture = capture_img()
     #               if capture:
      #                  email_conn()
    except:
        pass


def app_update():
     global data
     while True:
        time.sleep(5)
        if data:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s',(data['username'],))
            status = cursor.fetchone()
            details = status[3:8]
            bulb_ = Bulb(details)
            temp_sensor = DhtSensor()
            temp_readings = temp_sensor.update_readings()
            cursor.execute('UPDATE users SET temp = %s and humidity = %s WHERE username = %s',(temp_readings['temperature'],temp_readings['humidity'],data['username']))
            conn.close()
        else:
             print('Waiting for user to enter.')



def main1():
    thread1 = threading.Thread(target=init_rfid)
    thread2 = threading.Thread(target=intrusion_detect)
    thread3 = threading.Thread(target = app_update) 


    thread1.start()
    thread2.start()
    #thread3.start()

    thread1.join()
    thread2.join()
    app_update()

    print('both functions completed')


if __name__ == '__main__':
    main1()

        
