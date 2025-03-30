import time
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.config import Config
import paho.mqtt.client as mqtt
from discovery import discover_mqtt
import os

# Don't show mouse cursor
Config.set('graphics', 'show_cursor', '0')

DEVICE_ID = os.getenv("DEVICE_ID", "fallback")
BROKER_IP = os.getenv("BROKER_IP") or discover_mqtt()

# Global MQTT client
client = mqtt.Client()

# Screen Definitions
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='horizontal', padding=40, spacing=20)

        # Left 2/3 – Clock (placeholder for now)
        clock = Label(text="🕒", font_size='120sp')
        layout.add_widget(clock)

        # Right 1/3 – Buttons
        btns = BoxLayout(orientation='vertical', spacing=20)
        request_btn = Button(text="Request", size_hint=(1, 0.5), font_size='32sp')
        release_btn = Button(text="Release", size_hint=(1, 0.5), font_size='32sp')
        request_btn.bind(on_press=self.request_site)
        release_btn.bind(on_press=self.release_site)
        btns.add_widget(request_btn)
        btns.add_widget(release_btn)
        layout.add_widget(btns)

        self.add_widget(layout)

    def request_site(self, instance):
        print("📤 Requesting site...")
        client.publish("yard/request", DEVICE_ID)

    def release_site(self, instance):
        print("📤 Releasing site...")
        client.publish("yard/release", DEVICE_ID)

class ReservedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout()
        label = Label(text="BUSY", font_size='72sp', color=(1, 1, 1, 1))
        self.add_widget(layout)
        layout.add_widget(label)
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 0, 0, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

class InUseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        label = Label(text="IN USE", font_size='72sp', color=(1, 1, 1, 1))
        done_btn = Button(text="Done", size_hint=(1, 0.2), font_size='32sp')
        done_btn.bind(on_press=self.release)
        layout.add_widget(label)
        layout.add_widget(done_btn)
        self.add_widget(layout)

        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 1, 0, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)

    def release(self, *args):
        print("📤 Done — releasing site")
        client.publish("yard/release", DEVICE_ID)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

# Screen Manager App
class DogYardApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(ReservedScreen(name="reserved"))
        self.sm.add_widget(InUseScreen(name="inuse"))
        return self.sm

    def on_start(self):
        threading.Thread(target=self.connect_and_listen, daemon=True).start()

    def connect_and_listen(self):
        broker = discover_mqtt()
        if not broker:
            print("❌ Could not find MQTT broker.")
            return

        def on_connect(client, userdata, flags, rc):
            print(f"✅ Connected to broker at {broker}")
            client.subscribe("yard/state")

        def on_message(client, userdata, msg):
            state = msg.payload.decode()
            print(f"📥 Received state: {state}")

            if state == "free":
                self.sm.current = "main"
            elif state == DEVICE_ID:
                self.sm.current = "inuse"
            else:
                self.sm.current = "reserved"

        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(broker, 1883, 60)
            client.loop_forever()
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")

if __name__ == "__main__":
    DogYardApp().run()
