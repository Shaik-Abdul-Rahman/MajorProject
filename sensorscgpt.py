import Adafruit_DHT
from gpiozero import DistanceSensor
from RPi import GPIO
from mfrc522 import SimpleMFRC522

class DhtSensor:
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 17

    def update_readings(self):
        humidity, temp = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return {'humidity': humidity, 'temperature': temp}

class UltraSensor:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)
        self.sensor = DistanceSensor(echo=24, trigger=23)

    def update_distance(self):
        try:
            distance = self.sensor.distance
            return distance
        except Exception as e:
            print('Error occurred in reading ultrasonic sensor:', e)
            return None

class SolenoidLock:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.gpio.setmode(GPIO.BCM)
        self.gpio.setup(18, GPIO.OUT)

    def update_lock(self, status):
        if status == 'Lock':
            self.gpio.output(18, 1)
            return 'Locked Successfully'
        else:
            self.gpio.output(18, 0)
            return 'Unlocked Successfully'

class Bulb:
    def __init__(self, statuses):
        self.pins = [17, 27, 22, 5, 18]
        self.statuses = statuses
        GPIO.setmode(GPIO.BCM)
        for pin, status in zip(self.pins, self.statuses):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)

    def update_system(self, new_values):
        for pin, status in zip(self.pins, new_values):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)

    def close_all(self):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)

    def change_status(self):
        GPIO.setup(18, GPIO.OUT)
        read = GPIO.input(18)
        GPIO.output(18, GPIO.HIGH if read == GPIO.LOW else GPIO.LOW)
        print('Unlocked' if read == GPIO.LOW else 'Locked')

    def unlock_lock(self):
        GPIO.output(18, GPIO.HIGH)

class RFID:
    def __init__(self):
        self.reader = SimpleMFRC522()

    def register(self, username):
        try:
            print('Place your tag...')
            self.id, self.text = self.reader.read()
            self.reader.write(username)
            print('Tag written successfully.')
            return {'update': 'success', 'id': self.id}
        finally:
            GPIO.cleanup()

    def read(self):
        try:
            print('Place your tag...')
            self.id, self.text = self.reader.read()
            print('Tag read successfully.')
            return {'id': self.id, 'username': self.text}
        finally:
            GPIO.cleanup()
