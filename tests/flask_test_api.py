"""
Lightweight Flask dev server — drop-in replacement for FastAPI while
uvicorn/pydantic-core is unavailable. Run with: python api/dev_server.py
"""

import time
import serial
from flask import Flask, jsonify
from flask_cors import CORS

PORT = "COM4"
BAUD_RATE = 9600

app = Flask(__name__)
CORS(app)  # allow the React dev server (localhost:5173) to call this


def _send(arduino, cmd):
    arduino.write((cmd + "\n").encode("utf-8"))
    return arduino.readline().decode("utf-8").strip()


@app.post("/control/start")
def start():
    try:
        arduino = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
    except serial.SerialException as e:
        return jsonify({"detail": str(e)}), 503

    try:
        _send(arduino, "MAGNET ON")
        time.sleep(0.5)
        _send(arduino, "MOVE 2 220")
        time.sleep(2)
        _send(arduino, "MOVE 1 200")
        time.sleep(2)
        _send(arduino, "MAGNET OFF")
    finally:
        arduino.close()

    return jsonify({"status": "done"})


@app.post("/control/move")
def move():
    from flask import request
    body = request.get_json()
    channel = body["channel"]
    angle = body["angle"]

    try:
        arduino = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
    except serial.SerialException as e:
        return jsonify({"detail": str(e)}), 503

    try:
        resp = _send(arduino, f"MOVE {channel} {angle}")
    finally:
        arduino.close()

    return jsonify({"status": "ok", "response": resp})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
