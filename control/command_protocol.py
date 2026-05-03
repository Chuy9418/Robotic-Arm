# control/command_protocol.py

BAUD_RATE = 9600

MIN_ANGLE = 0
MAX_ANGLE = 180
MIN_CHANNEL = 0
MAX_CHANNEL = 15


def validate_channel(channel: int) -> None:
    if not MIN_CHANNEL <= channel <= MAX_CHANNEL:
        raise ValueError(f"Channel must be between {MIN_CHANNEL} and {MAX_CHANNEL}")


def validate_angle(angle: int) -> None:
    if not MIN_ANGLE <= angle <= MAX_ANGLE:
        raise ValueError(f"Angle must be between {MIN_ANGLE} and {MAX_ANGLE}")


def build_command(channel: int, angle: int) -> str:
    validate_channel(channel)
    validate_angle(angle)
    return f"MOVE {channel} {angle}\n"
