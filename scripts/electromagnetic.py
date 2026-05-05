import serial
import time

PORT = "COM3"
BAUD_RATE = 9600

arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)

print("Turning magnet ON")
arduino.write(b"MAGNET ON\n")
print("Arduino:", arduino.readline().decode().strip())

time.sleep(8)

print("Turning magnet OFF")
arduino.write(b"MAGNET OFF\n")
print("Arduino:", arduino.readline().decode().strip())

arduino.close()