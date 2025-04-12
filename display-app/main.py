import os

import httpx
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from config import DEVICE_ID, SERVER_URL
from screens.busy_screen import ReservedScreen
from screens.inuse_screen import InUseScreen
from screens.main_screen import MainScreen


Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)

class ClockButtonApp(App):
    def build(self):
        print(f"📡 Using server at {SERVER_URL}")
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main", switch_callback={
            "request": self.request_access,
            "release": self.release_access
        }))
        self.sm.add_widget(ReservedScreen(name="busy"))
        self.sm.add_widget(InUseScreen(name="inuse", done_callback=self.release_access))
        self.sm.current = "main"
        Clock.schedule_interval(self.check_state, 2)
        return self.sm

    def switch_to(self, name):
        Clock.schedule_once(lambda dt: setattr(self.sm, "current", name), 0)

    def request_access(self, *args):
        print(f"🟢 UI ({DEVICE_ID}) requesting access...")
        # Trigger button feedback
        screen = self.sm.get_screen("main")
        screen.show_requesting_state()
        try:
            httpx.post(f"{SERVER_URL}/request", json={"device_id": DEVICE_ID}, timeout=2)
        except Exception as e:
            print("⚠️ Request failed:", e)
            screen.reset_request_button()

    def release_access(self, *args):
        print(f"🔴 UI ({DEVICE_ID}) releasing access...")
        try:
            httpx.post(f"{SERVER_URL}/release", json={"device_id": DEVICE_ID}, timeout=2)
        except Exception as e:
            print("⚠️ Release failed:", e)

    def check_state(self, dt):
        try:
            r = httpx.get(f"{SERVER_URL}/state", timeout=2)
            if r.status_code == 200:
                state = r.json()
                occupied_by = state.get("occupied_by")
                print(f"📥 Server state: occupied_by = {occupied_by}")

                if occupied_by is None:
                    self.switch_to("main")
                    screen = self.sm.get_screen("main")
                    screen.reset_request_button()

                elif occupied_by == DEVICE_ID:
                    self.switch_to("inuse")

                else:
                    self.switch_to("busy")
        except Exception as e:
            print("⚠️ Failed to get state:", e)


if __name__ == "__main__":
    ClockButtonApp().run()
