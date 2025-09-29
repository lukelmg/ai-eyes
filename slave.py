import socket
import json
import os
import subprocess

os.environ['DISPLAY'] = ':0'
subprocess.run(['xhost', '+local:'], capture_output=True)
import pyautogui

HOST = '0.0.0.0'
PORT = 5555

def handle_command(cmd):
    action = cmd.get('action')
    if action == 'move':
        pyautogui.moveTo(cmd['x'], cmd['y'])
    elif action == 'click':
        pyautogui.click()
    elif action == 'type':
        pyautogui.write(cmd['text'])
    elif action == 'get_screen':
        w, h = pyautogui.size()
        print(f"Screen: {w}x{h}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    sock.bind(('', PORT))
    sock.listen(1)
except OSError as e:
    print(f"Error binding to port {PORT}: {e}")
    print("Port might be in use. Wait 60 seconds or run: sudo fuser -k 5555/tcp")
    exit(1)

print(f"Slave listening on {PORT}...")

while True:
    conn, addr = sock.accept()
    print(f"Connected: {addr}")
    buffer = ""
    while True:
        data = conn.recv(1024)
        if not data:
            break
        buffer += data.decode()
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            cmd = json.loads(line)
            handle_command(cmd)
    conn.close()
