import RPi.GPIO as GPIO
import time

# Set up GPIO mode and pin number
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

# Toggle the GPIO pin
try:
    while True:
        GPIO.output(17, GPIO.HIGH)  # Turn ON
        time.sleep(1)
        GPIO.output(17, GPIO.LOW)   # Turn OFF
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()  # Cleanup GPIO settings on program exit
