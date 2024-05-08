from sensors import *
from picamera import PiCamera
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import RPi.GPIO as gpio


URL = 'HELLO HOW ARE YOU'


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
            gpio.add_event_detect(BUTTON_PIN,gpio.FALLING, callback= button_pressed,bouncetime=200)
            if dist < 0.5:
                time.sleep(10)
                dist = ultra_dist.update_distance()
                if dist < 0.9:
                    capture = capture_img()
                    if capture:
                        email_conn()
        finally:
            gpio.cleanup()




def button_pressed(channel):
	print('button pressed')
	gpio.setup(26,gpio.OUT)
	state = gpio.input(26)
	if state == gpio.LOW:
		gpio.output(26,gpio.HIGH)
	else:
		gpio.output(26,gpio.LOW)



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

	


solenoid_check()

