import Adafruit_DHT
from gpiozero import DistanceSensor
from time import sleep
from RPi import GPIO
from mfrc522 import SimpleMFRC522

URL = 'https://lionfish-intent-nicely.ngrok-free.app'

class DhtSensor:
    def __init__(self):
        self.gpio = GPIO
        self.gpio.setwarnings(False)
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
        

class Appliances:
    def __init__(self, status):
        self.pins = [6,13,19,18,26]
        self.status = status
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        try:
            for pin, stat in zip(self.pins, self.status):
                GPIO.setup(pin,GPIO.OUT)
                GPIO.output(pin,GPIO.HIGH if stat else GPIO.LOW)
        finally:
            #GPIO.cleanup()
            print('appliances restored succesfully.')


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
