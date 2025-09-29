import socket
import json
import time

HOST = '192.168.68.75'  # Change to slave's IP
PORT = 5555

def send_command(sock, command):
    sock.sendall(json.dumps(command).encode() + b'\n')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Get screen dimensions and move to center
send_command(sock, {"action": "get_screen"})
time.sleep(0.1)

# Assume 1920x1080, adjust if needed
import math
cx, cy = 960, 540
radius = 200

# Move to center
send_command(sock, {"action": "move", "x": cx, "y": cy})
time.sleep(0.5)

# Circle motion
for i in range(100):
    angle = (i / 100) * 2 * math.pi
    x = int(cx + radius * math.cos(angle))
    y = int(cy + radius * math.sin(angle))
    send_command(sock, {"action": "move", "x": x, "y": y})
    time.sleep(0.01)

sock.close()