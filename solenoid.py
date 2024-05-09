from sensors import *
import time

pin = [0,0,0,0,0]
bulb_ = Bulb(pin)

#bulb_.unlock_lock()
while True:
	bulb_.change_status()
	time.sleep(3)

