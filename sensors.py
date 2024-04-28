import Adafruit_DHT
from gpiozero import DistanceSensor
from time import sleep
from RPi import GPIO

class DhtSensor:
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 21

    def UpdateRead(self):
        self.humidity, self.temp = Adafruit_DHT.read_retry(self.sensor, self.pin)

        return {'humidity': self.humidity,'temp': self.temp}
    
     
class UltraSensor:

    def __init__(self):
        self.sensor = DistanceSensor(23,24)

    def UpdateDist(self):
        self.distance = self.sensor.distance
        sleep(0.5)
        return self.distance
    


class SolenoidLock():

    def __init__(self):
        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.setmode(self.gpio.BCM)
        self.gpio.setup(18,self.gpio.OUT)


    def UpdateLock(self,status):
        if status == 'Lock':
            self.gpio.output(18,1)
            sleep(1)
            return 'Locked Succesfully'
        
        else:
            self.gpio.output(18,0)
            sleep(1)
            return 'UnLocked Succesfully'
