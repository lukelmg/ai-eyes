import socket
import json
import time

HOST = '192.168.68.75'  # Change to slave's IP
PORT = 5555

def send_command(sock, command):
    sock.sendall(json.dumps(command).encode() + b'\n')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Example commands
send_command(sock, {"action": "move", "x": 500, "y": 300})
time.sleep(1)
send_command(sock, {"action": "click"})
time.sleep(1)
send_command(sock, {"action": "type", "text": "Hello from master"})

sock.close()