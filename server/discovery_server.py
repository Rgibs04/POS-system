import socket
import threading
import time

def discovery_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 5001))
    print("Discovery server listening on port 5001")
    while True:
        data, addr = sock.recvfrom(1024)
        if data == b"DISCOVER_POS_SERVER":
            sock.sendto(b"POS_SERVER_HERE", addr)
            print(f"Responded to discovery from {addr}")

if __name__ == '__main__':
    threading.Thread(target=discovery_server, daemon=True).start()
    # Keep running
    while True:
        time.sleep(1)
