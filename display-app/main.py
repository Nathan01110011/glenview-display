import os
import httpx
import toml
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from screens.busy_screen import ReservedScreen
from screens.inuse_screen import InUseScreen
from screens.main_screen import MainScreen
from network_discovery import find_server_on_lan

Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)

# Load device-specific config
DEVICE_ID = os.getenv("DEVICE_ID", "default2")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "dog_config", f"{DEVICE_ID}.toml")
DOG_CONFIG = toml.load(CONFIG_PATH)

DOG_NAME = DOG_CONFIG["dog_name"]
DOG_IMAGES = DOG_CONFIG["images"]
THEME_COLOR = DOG_CONFIG.get("theme_color", [0, 0.6, 0, 1])

OTHER_DOG_NAME = DOG_CONFIG["other_dog"]["name"]
OTHER_DOG_IMAGES = DOG_CONFIG["other_dog"]["images"]


class ClockButtonApp(App):
    def build(self):
        # Set up UI
        self.sm = ScreenManager()
        self.main_screen = MainScreen(name="main", switch_callback={
            "request": self.request_access,
            "release": self.release_access
        })
        self.reserved_screen = ReservedScreen(name="busy")
        self.inuse_screen = InUseScreen(name="inuse", done_callback=self.release_access)

        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.reserved_screen)
        self.sm.add_widget(self.inuse_screen)
        self.sm.current = "main"

        # Detect server
        env_override = os.getenv("SERVER_IP")
        self.server_ip = env_override or find_server_on_lan() or "localhost"
        print(f"📡 Using server at http://{self.server_ip}:8000")

        # Tell the weather bar what server to use
        self.main_screen.weather_bar.set_server_url(f"http://{self.server_ip}:8000")

        Clock.schedule_interval(self.check_state, 2)
        return self.sm

    def get_server_url(self, path: str) -> str:
        return f"http://{self.server_ip}:8000{path}"

    def switch_to(self, name):
        Clock.schedule_once(lambda dt: setattr(self.sm, "current", name), 0)

    def request_access(self, *args):
        print(f"🟢 UI ({DEVICE_ID}) requesting access...")
        self.main_screen.show_requesting_state()
        try:
            httpx.post(self.get_server_url("/request"), json={"device_id": DEVICE_ID}, timeout=2)
        except Exception as e:
            print("⚠️ Request failed:", e)
            self.main_screen.reset_request_button()
            self.try_rescan_server()

    def release_access(self, *args):
        print(f"🔴 UI ({DEVICE_ID}) releasing access...")
        try:
            httpx.post(self.get_server_url("/release"), json={"device_id": DEVICE_ID}, timeout=2)
        except Exception as e:
            print("⚠️ Release failed:", e)
            self.try_rescan_server()

    def check_state(self, dt):
        try:
            r = httpx.get(self.get_server_url("/state"), timeout=2)
            if r.status_code == 200:
                state = r.json()
                occupied_by = state.get("occupied_by")
                start_time = state.get("start_time")
                print(f"📥 Server state: occupied_by = {occupied_by} — start_time = {start_time}")

                if occupied_by is None:
                    self.switch_to("main")
                    self.main_screen.reset_request_button()

                elif occupied_by == DEVICE_ID:
                    self.inuse_screen.set_content(DOG_NAME, DOG_IMAGES, THEME_COLOR, start_time=start_time)
                    self.switch_to("inuse")

                else:
                    self.reserved_screen.set_content(OTHER_DOG_NAME, OTHER_DOG_IMAGES, start_time=start_time)
                    self.switch_to("busy")

                # Trigger weather retry if needed
                if hasattr(self.main_screen, "weather_bar"):
                    self.main_screen.weather_bar.retry_weather_if_needed(self.get_server_url("/weather"))

        except Exception as e:
            print("⚠️ Failed to get state:", e)
            self.try_rescan_server()

    def try_rescan_server(self):
        new_ip = find_server_on_lan()
        if new_ip and new_ip != self.server_ip:
            print(f"🔁 Server rediscovered at new IP: {new_ip}")
            self.server_ip = new_ip
            self.main_screen.weather_bar.set_server_url(f"http://{self.server_ip}:8000")


if __name__ == "__main__":
    ClockButtonApp().run()
