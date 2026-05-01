# The real controller (talks to Arduino over serial) + a mock for testing without hardware

# control/arm_controller.py

import serial
import time
from control.command_protocol import BAUD_RATE, build_command


class ArmController:
    def __init__(self, port: str = "/dev/ttyACM0"):
        self.ser = serial.Serial(port, BAUD_RATE, timeout=2)
        time.sleep(2)  # Wait for Arduino to reset

    def move(self, channel: int, angle: int) -> str:
        cmd = build_command(channel, angle)
        self.ser.write(cmd.encode())
        response = self.ser.readline().decode().strip()
        return response

    def close(self):
        self.ser.close()


class MockArmController:
    """Use this when no Arduino is connected — for pipeline testing."""
    def move(self, channel: int, angle: int) -> str:
        print(f"[MOCK] Channel {channel} -> {angle} degrees")
        return f"OK:{channel}"

    def close(self):
        pass