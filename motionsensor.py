from gpiozero import LED, MotionSensor

led = LED(13)

pir = MotionSensor(6)
led.off()

while True:
    
    pir.wait_for_motion()
    print('motion detected')
    led.on()
    pir.wait_for_no_motion()
    led.off()
    print('motion stopped')
    