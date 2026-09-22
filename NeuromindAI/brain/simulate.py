import serial
import time

# Connect to Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2)

def decide_move(front, left, right):
    """Simple SERAI reasoning simulation"""
    if front < 20:
        if left > right:
            return 'L'
        else:
            return 'R'
    else:
        return 'F'

while True:
    line = arduino.readline().decode().strip()
    if line.startswith("FRONT"):
        # Parse sensor values
        data = line.split()
        front = int(data[0].split(":")[1])
        left = int(data[1].split(":")[1])
        right = int(data[2].split(":")[1])

        # AI Decision
        decision = decide_move(front, left, right)
        arduino.write(decision.encode())
