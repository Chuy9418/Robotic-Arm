import serial
import time

PORT = "COM4"
BAUD_RATE = 9600


def send_command(arduino, command):
    print(f"Sending: {command}")
    arduino.write((command + "\n").encode("utf-8"))
    response = arduino.readline().decode("utf-8").strip()
    print("Arduino:", response)
    time.sleep(0.5)


arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# Turn magnet on
send_command(arduino, "MAGNET ON")

# RESET
send_command(arduino, "MOVE 2 220")
time.sleep(2)
send_command(arduino, "MOVE 1 200")
time.sleep(2)
send_command(arduino, "MOVE 0 60")
time.sleep(2)



# Turn magnet off
send_command(arduino, "MAGNET OFF")

arduino.close()
