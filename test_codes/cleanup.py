import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print('place your card')
    id, text = reader.read()
    data['id'] = id
    data['username'] = text
    print(id,text)
    
finally:
    gpio.cleanup()

