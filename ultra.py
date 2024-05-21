from sensors import UltraSensor
import time
#from RPi import GPIO


#GPIO.cleanup()
#ult = UltraSensor()
#while True:
   # time.sleep(2)
   
  #  dist = ult.update_dist()
 #   print(dist)


def read_di(sensor):
	while True:
		distance = sensor.update_dist()
		print(distance)
		time.sleep(1)


if __name__ == '__main__':
	ultra_sensor = UltraSensor()
	read_di(ultra_sensor)

