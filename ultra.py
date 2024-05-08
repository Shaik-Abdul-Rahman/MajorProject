from sensors import UltraSensor

ult = UltraSensor()

while True:
	data = ult.update_distance()
	print(data)
