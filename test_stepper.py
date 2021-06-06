import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

halfstep_seq = [
    [1,0,0,0], #N
    [1,1,0,0], #NE  
    [0,1,0,0], #E
    [0,1,1,0], #SE  
    [0,0,1,0], #S
    [0,0,1,1], #SW 
    [0,0,0,1], #W
    [1,0,0,1] #NW
]

control_pins = [7, 11, 13, 15]
control_pins2 = [31, 33, 35, 37]

for pin in control_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)
  
for pin in control_pins2:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

def step(n):
    for i in range(n):
        for halfstep in range(len(halfstep_seq)):
            for pin in range(4):
                GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
                GPIO.output(control_pins2[pin], halfstep_seq[halfstep][pin])
            time.sleep(.001)

if __name__ == "__main__":
    for num in range(288):
        step(8)
#GPIO.cleanup()
