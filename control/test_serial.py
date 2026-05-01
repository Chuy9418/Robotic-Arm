# control/command_protocol.py

BAUD_RATE = 9600

def build_command(channel: int, angle: int) -> str:
    """Format: 'CH:ANGLE\n'  e.g. '0:90\n'"""
    angle = max(0, min(180, angle))
    return f"{channel}:{angle}\n"