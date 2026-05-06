"""
Keyboard control for the robotic arm.
Run with: python scripts/keyboard_control.py

  A / D  →  Wrist      (channel 0)  left / right
  W / S  →  Elbow  (channel 1)  up   / down
  Q / E  →  Shoulder     (channel 2)  up   / down
  Z / X  →  Base     (channel 3)  up   / down
  M      →  Magnet toggle
  H      →  Home all servos (90°)
  Esc    →  Quit
"""

import msvcrt
import time
import serial

PORT = "COM3"
BAUD_RATE = 9600
STEP = 5  # degrees per keypress
LIMITS = (0, 180)


def clamp(val):
    return max(LIMITS[0], min(LIMITS[1], val))


def send(arduino, cmd):
    arduino.write((cmd + "\n").encode("utf-8"))
    arduino.readline()


def print_state(angles, magnet):
    print(
        f"\r  Base:{angles[0]:>4}°  Shoulder:{angles[1]:>4}°"
        f"  Elbow:{angles[2]:>4}°  Wrist:{angles[3]:>4}°"
        f"  Magnet:{'ON ' if magnet else 'OFF'}   ",
        end="",
        flush=True,
    )


def main():
    print(f"Connecting to {PORT}...")
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=2)
    time.sleep(2)
    print("Connected. Use WASDQEZXMH to control. Esc to quit.\n")

    angles = {0: 90, 1: 90, 2: 90, 3: 90}
    magnet = False

    # Home on start
    for ch, ang in angles.items():
        send(arduino, f"MOVE {ch} {ang}")

    print_state(angles, magnet)

    keymap = {
        "a": (0, +STEP), "d": (0, -STEP),
        "w": (1, +STEP), "s": (1, -STEP),
        "q": (2, +STEP), "e": (2, -STEP),
        "z": (3, +STEP), "x": (3, -STEP),
    }

    while True:
        key = msvcrt.getwch().lower()

        if key == "\x1b":  # Esc
            break
        elif key in keymap:
            ch, delta = keymap[key]
            angles[ch] = clamp(angles[ch] + delta)
            send(arduino, f"MOVE {ch} {angles[ch]}")
        elif key == "m":
            magnet = not magnet
            send(arduino, "MAGNET ON" if magnet else "MAGNET OFF")
        elif key == "h":
            angles = {0: 90, 1: 90, 2: 90, 3: 90}
            for ch, ang in angles.items():
                send(arduino, f"MOVE {ch} {ang}")

        print_state(angles, magnet)

    print("\nClosing.")
    arduino.close()


if __name__ == "__main__":
    main()
