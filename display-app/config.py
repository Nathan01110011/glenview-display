import os

DEVICE_ID = os.getenv("DEVICE_ID", "frame2")
SERVER_IP = os.getenv("SERVER_IP", "localhost")
SERVER_URL = "http://localhost:8000"  # Default fallback


def set_server_ip(ip):
    global SERVER_URL
    SERVER_URL = f"http://{ip}:8000"