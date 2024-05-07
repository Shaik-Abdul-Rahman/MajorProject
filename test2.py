import RPi.GPIO as gpio
from time import sleep

gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

gpio.setup(18,gpio.OUT)

while (True):
	print('0')
	gpio.output(18,0)
	sleep(5)
	print('1')
	gpio.output(18,1)
	sleep(5)
