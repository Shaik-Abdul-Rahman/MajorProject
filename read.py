import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
	id, text = reader.read()
	print(id)
	print(text)
finally:
	gpio.cleanup()
