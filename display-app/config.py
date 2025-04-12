import os

DEVICE_ID = os.getenv("DEVICE_ID", "frame2")
SERVER_IP = os.getenv("SERVER_IP", "localhost")
SERVER_URL = f"http://{SERVER_IP}:8000"
