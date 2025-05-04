# display-app/config.py

import os
import toml


class Config:
    DEVICE_ID = os.getenv("DEVICE_ID", "default2")
    SERVER_IP = os.getenv("SERVER_IP", "localhost")
    SERVER_URL = f"http://{SERVER_IP}:8000"

    DOG_NAME = None
    DOG_IMAGES = []
    THEME_COLOR = [0, 0.6, 0, 1]
    OTHER_DOG_NAME = None
    OTHER_DOG_IMAGES = []
    IS_SERVER = False

    @classmethod
    def set_server_ip(cls, ip: str):
        cls.SERVER_IP = ip
        cls.SERVER_URL = f"http://{ip}:8000"

    @classmethod
    def load_dog_config(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "dog_config", f"{cls.DEVICE_ID}.toml")
        data = toml.load(config_path)

        cls.DOG_NAME = data.get("dog_name")
        cls.DOG_IMAGES = data.get("images", [])
        cls.THEME_COLOR = data.get("theme_color", [0, 0.6, 0, 1])
        cls.OTHER_DOG_NAME = data.get("other_dog", {}).get("name")
        cls.OTHER_DOG_IMAGES = data.get("other_dog", {}).get("images", [])
        cls.IS_SERVER = data.get("is_server", False)
