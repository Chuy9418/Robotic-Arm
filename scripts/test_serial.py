# scripts/test_serial.py

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import time
import argparse
from control.arm_controller import ArmController, MockArmController


def run_test(controller, channel: int = 0):
    print(f"=== Servo Test — Channel {channel} ===\n")

    steps = [
        (90, "CENTER"),
        (70, "SMALL LEFT / DOWN"),
        (90, "CENTER"),
        (110, "SMALL RIGHT / UP"),
        (90, "CENTER — reset"),
    ]

    for angle, label in steps:
        print(f"-> {label}")
        response = controller.move(channel, angle)
        print(f"   Arduino: {response}")
        time.sleep(1.2)

    print("\n=== Test complete ===")
    controller.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run without hardware")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Arduino serial port")
    parser.add_argument("--channel", type=int, default=0, help="PCA9685 channel")
    args = parser.parse_args()

    controller = MockArmController() if args.mock else ArmController(port=args.port)
    run_test(controller, channel=args.channel)
