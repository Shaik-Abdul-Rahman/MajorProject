import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
#from sensors import *


reader = SimpleMFRC522()

try:
	print('place the card')
	id,text = reader.read()
	print(id)
	print(text)
finally:
	gpio.cleanup()
