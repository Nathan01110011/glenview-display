# display-app/config.py

import os


class Config:
    DEVICE_ID = os.getenv("DEVICE_ID", "frame2")
    SERVER_IP = os.getenv("SERVER_IP", "localhost")
    SERVER_URL = f"http://{SERVER_IP}:8000"

    @classmethod
    def set_server_ip(cls, ip: str):
        cls.SERVER_IP = ip
        cls.SERVER_URL = f"http://{ip}:8000"
