from sensors import *
import cv2
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os


def capture_img():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print('Camera not detected.')
        camera.release()
        return False
    
    ret, frame = camera.read()

    if not ret:
        print('Not able to read the frame')
        camera.release()
        return False
    
    camera.release()
    cv2.imwrite('image.jpg',frame)
    print('Image captured successfully.')
    return True 
   

def email_conn():
    sender_email = "mohammad.ahmed1774@gmail.com"
    receiver_email = "mohammad.ahmed1774@gmail.com"
    password = ""

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "Intrusion Detection"

    # Add body to email
    body = ""
    message.attach(MIMEText(body, 'plain'))

def main():
    ultra_dist = UltraSensor()
    distance = ultra_dist.update_distance()
    if distance> 0.5:
        time.sleep(4)
        image_captured = capture_img()
        while not image_captured:




if __name__ == '__main__':
    main()