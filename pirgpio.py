import RPi.GPIO as gpio
import time
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
pin = 23
gpio.setup(pin,gpio.OUT)
while(1):
	if gpio.input(pin) == gpio.HIGH:
		print('motion')
	else:
		print('no motion')
		time.sleep(1)
