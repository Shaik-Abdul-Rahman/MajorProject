import Adafruit_DHT
from gpiozero import DistanceSensor
from time import sleep
from RPi import GPIO
from mfrc522 import SimpleMFRC522

URL = 'https://lionfish-intent-nicely.ngrok-free.app'

class DhtSensor:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setmode(self.gpio.BCM)
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 17

    def update_readings(self):
        humidity, temp = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return {'humidity': humidity, 'temperature': temp}
    def cleanup(self):
        self.gpio.cleanup(self.pin)
        

class UltraSensor:
    def __init__(self):
        #self.sensor = DistanceSensor(echo=24, trigger=23)
        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)
        self.sensor2 = None
        self.trigger_pin = 23
        self.echo_pin = 24
        
    def update_dist(self):
        try:
            if self.sensor2 is None:
                self.sensor2 = DistanceSensor(echo=24, trigger=23)
            distance = self.sensor2.distance
            sleep(0.5)
    #        self.gpio.cleanup()
            return distance
        except Exception as e:
            print('Error Occured in reading ultrasonic sensor : ',e)
        
    def cleanup(self):
        if self.sensor2 is not None:
            self.sensor2.close()
        self.gpio.cleanup([23,24])
        

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

class Appliances:
    def __init__(self, status):
        self.pins = [6,13,19,26,18]
        self.status = status
        GPIO.setmode(GPIO.BCM)
        try:
            for pin, stat in zip(self.pins, self.status):
                GPIO.setup(pin,GPIO.OUT)
                GPIO.output(pin,GPIO.HIGH if stat else GPIO.LOW)
        finally:
            #GPIO.cleanup()
            print('appliances restored succesfully.')

class Bulb:
    def __init__(self, statuses):
        self.pins = [17, 27, 22, 5, 18]
        self.statuses = statuses
        GPIO.setmode(GPIO.BCM)
        for pin, status in zip(self.pins, self.statuses):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)
    def update_system(self,new_values):
        for pin, status in zip(self.pins, new_values):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)

    def close_all(self):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)

    def change_status(self):
        GPIO.setup(18,GPIO.OUT)
        read = GPIO.input(18)

        GPIO.output(18, GPIO.HIGH if read == GPIO.LOW else GPIO.LOW)
        print('Unlocked' if read == GPIO.LOW else 'Locked')
    def unlock_lock(self):
        GPIO.output(18,GPIO.HIGH)

class rfid:

    def __init___(self):
        #self.reader = SimpleMFRC522()
        pass

    def register(self,username):
        try:
            print('place your tag')
            reader = SimpleMFRC522()
            self.id, self.text = reader.read()
            reader.write(username)
            print('written')
            return {'update':'success','id':self.id}

        finally:
            GPIO.cleanup()
    def read(self):
        try:
            print('Place your tag.')
            reader = SimpleMFRC522()
            print('testing1')
            self.id, self.text = reader.read()
            print('testing2')
            print('successfully read.')
            print(type(self.id))

            return {'id':self.id,'username':self.text}
        finally:
            GPIO.cleanup()
