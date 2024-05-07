import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import cv2

# Email configuration
sender_email = "mohammad.ahmed1774@gmail.com"
receiver_email = "mohammad.ahmed1774@gmail.com"
password = "tmbncjxadrbzrnvx"

# Create the email message
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = "Subject of the Email"

# Add body to email
body = "This is the body of the email."
message.attach(MIMEText(body, 'plain'))

def capture_and_save_image(filename='captured_image.jpg'):
    # Open the default camera (usually the webcam, camera index 0)
    camera = cv2.VideoCapture(1)

    # Check if the camera is opened successfully
    if not camera.isOpened():
        print("Error: Unable to open camera.")
        return

    # Read a frame from the camera
    ret, frame = camera.read()

    # Check if the frame was successfully captured
    if not ret:
        print("Error: Unable to capture frame.")
        camera.release()
        return

    # Release the camera
    camera.release()

    # Save the captured frame as an image file
    cv2.imwrite(filename, frame)
    print(f"Image captured and saved as '{filename}'.")

capture_and_save_image('image.jpg')

# Attach image file
image_path = "image.jpg"  # Change this to the path of your image file
if os.path.exists(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        image = MIMEImage(image_data, name=os.path.basename(image_path))
        message.attach(image)
else:
    print(f"Image file '{image_path}' not found.")

# Connect to the SMTP server and send email
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email. Error: {e}")
