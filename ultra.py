from sensors import UltraSensor
import time

while True:
    time.sleep(2)
    ult = UltraSensor()
    dist = ult.update_dist()
    print(dist)

