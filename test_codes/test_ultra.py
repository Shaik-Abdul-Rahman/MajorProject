import pigpio
import time

pi = pigpio.pi()

TRIG_PIN = 23
ECHO_PIN = 24

pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)

try:
    while True:
        pi.write(TRIG_PIN, pigpio.HIGH)
        time.sleep(0.00001)
        pi.write(TRIG_PIN, pigpio.LOW)

        start = time.time()
        while pi.read(ECHO_PIN) == 0:
            start = time.time()

        stop = time.time()
        while pi.read(ECHO_PIN) == 1:
            stop = time.time()

        elapsed = stop - start

        speed_of_sound = 343  # Speed of sound in meters per second
        distance = (elapsed * speed_of_sound) / 2

        print("Distance:", distance, "meters")
        time.sleep(1)

except KeyboardInterrupt:
    pass

pi.stop()
