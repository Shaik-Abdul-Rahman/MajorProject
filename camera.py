from picamera import PiCamera
import time
camera = PiCamera()

try:
	camera.start_preview()
	time.sleep(500)
	#camera.capture('img.jpg')

except KeyboardInterrupt:
	time.sleep(5)
	camera.capture('img.jpg')
	camera.stop_preview()
	camera.close()
 
