from gpiozero import MotionSensor
pir = MotionSensor(24)
while True:
	print('to detect')
	pir.wait_for_motion()
	print('you moved')
	pir.wait_for_no_motion()

