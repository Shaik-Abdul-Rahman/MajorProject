import pigpio
import RPi.GPIO as GPIO
import time
import threading

# Initialize pigpio
pi = pigpio.pi()

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 21
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ultrasonic sensor pins
TRIG_PIN = 23
ECHO_PIN = 24
pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)

# Function to read distance from ultrasonic sensor
def read_distance():
    try:
        while True:
            # Trigger ultrasonic sensor
            pi.write(TRIG_PIN, pigpio.HIGH)
            time.sleep(0.00001)
            pi.write(TRIG_PIN, pigpio.LOW)

            # Measure echo pulse duration
            start = time.time()
            while pi.read(ECHO_PIN) == 0:
                start = time.time()

            stop = time.time()
            while pi.read(ECHO_PIN) == 1:
                stop = time.time()

            elapsed = stop - start

            # Calculate distance
            speed_of_sound = 343  # Speed of sound in meters per second
            distance = (elapsed * speed_of_sound) / 2

            print("Distance:", distance, "meters")
            time.sleep(1)

    except KeyboardInterrupt:
        pass

# Function to handle button press
def button_pressed(channel):
    print("Button pressed")

# Add event detection for button press
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=200)

# Create and start thread for reading distance
distance_thread = threading.Thread(target=read_distance)
distance_thread.start()

try:
    # Keep the main thread running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    # Cleanup GPIO and pigpio
    GPIO.cleanup()
    pi.stop()
