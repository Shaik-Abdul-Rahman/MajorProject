import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
	text = input('new data')
	print('place your tag')
	reader.write(text)
	print('written')

finally:
	gpio.cleanup()
