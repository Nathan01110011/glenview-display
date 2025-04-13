import httpx
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from screens.busy_screen import ReservedScreen
from screens.inuse_screen import InUseScreen
from screens.main_screen import MainScreen
from network_discovery import find_server_on_lan
from config import Config

Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)

Config.load_dog_config()


class ClockButtonApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.main_screen = MainScreen(
            name="main",
            switch_callback={
                "request": self.request_access,
                "release": self.release_access,
            },
        )
        self.reserved_screen = ReservedScreen(name="busy")
        self.inuse_screen = InUseScreen(name="inuse", done_callback=self.release_access)

        self.server_ip = Config.SERVER_IP  # fallback until LAN scan runs

    def build(self):
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.reserved_screen)
        self.sm.add_widget(self.inuse_screen)
        self.sm.current = "main"

        discovered_ip = find_server_on_lan()
        self.server_ip = Config.SERVER_IP or discovered_ip or "localhost"
        Config.set_server_ip(self.server_ip)
        print(f"📡 Using server at {Config.SERVER_URL}")

        self.main_screen.weather_bar.set_server_url(Config.SERVER_URL)
        Clock.schedule_interval(self.check_state, 2)
        return self.sm

    def get_server_url(self, path: str) -> str:
        return f"http://{self.server_ip}:8000{path}"

    def switch_to(self, name):
        Clock.schedule_once(lambda _: setattr(self.sm, "current", name), 0)

    def request_access(self, *_):
        print(f"🟢 UI ({Config.DEVICE_ID}) requesting access...")
        self.main_screen.show_requesting_state()
        try:
            httpx.post(
                self.get_server_url("/request"),
                json={"device_id": Config.DEVICE_ID},
                timeout=2,
            )
        except httpx.RequestError as e:
            print("⚠️ Request failed:", e)
            self.main_screen.reset_request_button()
            self.try_rescan_server()

    def release_access(self, *_):
        print(f"🔴 UI ({Config.DEVICE_ID}) releasing access...")
        try:
            httpx.post(
                self.get_server_url("/release"),
                json={"device_id": Config.DEVICE_ID},
                timeout=2,
            )
        except httpx.RequestError as e:
            print("⚠️ Release failed:", e)
            self.try_rescan_server()

    def check_state(self, _):
        try:
            r = httpx.get(self.get_server_url("/state"), timeout=2)
            if r.status_code == 200:
                state = r.json()
                occupied_by = state.get("occupied_by")
                start_time = state.get("start_time")
                print(
                    f"📥 Server state: occupied_by = {occupied_by} — start_time = {start_time}"
                )

                if occupied_by is None:
                    self.switch_to("main")
                    self.main_screen.reset_request_button()
                elif occupied_by == Config.DEVICE_ID:
                    self.inuse_screen.set_content(
                        Config.DOG_NAME,
                        Config.DOG_IMAGES,
                        Config.THEME_COLOR,
                        start_time=start_time,
                    )
                    self.switch_to("inuse")
                else:
                    self.reserved_screen.set_content(
                        Config.OTHER_DOG_NAME,
                        Config.OTHER_DOG_IMAGES,
                        start_time=start_time,
                    )
                    self.switch_to("busy")

                if hasattr(self.main_screen, "weather_bar"):
                    self.main_screen.weather_bar.retry_weather_if_needed(
                        self.get_server_url("/weather")
                    )
        except httpx.RequestError as e:
            print("⚠️ Failed to get state:", e)
            self.try_rescan_server()

    def try_rescan_server(self):
        new_ip = find_server_on_lan()
        if new_ip and new_ip != self.server_ip:
            print(f"🔁 Server rediscovered at new IP: {new_ip}")
            self.server_ip = new_ip
            Config.set_server_ip(new_ip)
            self.main_screen.weather_bar.set_server_url(Config.SERVER_URL)


if __name__ == "__main__":
    ClockButtonApp().run()
