import machine
import time
led = machine.Pin(2,machine.Pin.OUT)
for i in range(4):
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)
