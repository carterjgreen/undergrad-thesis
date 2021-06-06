import RPi.GPIO as GPIO
import time

def onestep(distance=0.1):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    control_pins = [7,11,13,15]

    for pin in control_pins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)

    halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
    ]

    for i in range(8):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.001)

    GPIO.cleanup()

    return

if __name__ == "__main__":
    onestep()
