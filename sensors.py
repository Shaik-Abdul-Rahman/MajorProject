import Adafruit_DHT
from gpiozero import DistanceSensor
from time import sleep
from RPi import GPIO

class DhtSensor:
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 21

    def update_readings(self):
        humidity, temp = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return {'humidity': humidity, 'temp': temp}

class UltraSensor:
    def __init__(self):
        self.sensor = DistanceSensor(echo=24, trigger=23)

    def update_distance(self):
        distance = self.sensor.distance
        sleep(0.5)
        return distance

class SolenoidLock:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.gpio.setmode(GPIO.BCM)
        self.gpio.setup(18, GPIO.OUT)

    def update_lock(self, status):
        if status == 'Lock':
            self.gpio.output(18, 1)
            sleep(1)
            return 'Locked Successfully'
        else:
            self.gpio.output(18, 0)
            sleep(1)
            return 'Unlocked Successfully'

class Bulb:
    def __init__(self, statuses):
        self.pins = [17, 27, 22, 5, 18]
        GPIO.setmode(GPIO.BCM)
        for pin, status in zip(self.pins, statuses):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)
