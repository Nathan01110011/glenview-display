from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'show_cursor', '0')
Config.set('kivy', 'keyboard_mode', 'dock')
Config.set('kivy', 'keyboard_mode', 'system')

import os
import math
from datetime import datetime
import paho.mqtt.client as mqtt

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

# UI config
Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)

DEVICE_ID = os.getenv("DEVICE_ID", "frame1")
BROKER_IP = os.getenv("BROKER_IP", "localhost")

# ---------- UI Components ----------

class AnalogClock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            cx, cy = self.center
            r = min(self.width, self.height) / 2.2
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

            now = datetime.now()
            hour_angle = math.radians(((now.hour % 12 + now.minute / 60) / 12) * 360)
            min_angle = math.radians((now.minute / 60) * 360)
            sec_angle = math.radians((now.second / 60) * 360)

            Color(0, 0, 0)
            self.draw_hand(cx, cy, r * 0.5, hour_angle, 4)
            self.draw_hand(cx, cy, r * 0.7, min_angle, 3)
            Color(1, 0, 0)
            self.draw_hand(cx, cy, r * 0.9, sec_angle, 2)

    def draw_hand(self, cx, cy, length, angle, width):
        Line(points=[cx, cy, cx + length * math.sin(angle), cy + length * math.cos(angle)], width=width)


class StyledSquareButton(Button):
    def __init__(self, text='', background_color=(0.2, 0.6, 1, 1), on_press_callback=None, **kwargs):
        super().__init__(**kwargs)

        self.text = text
        self.font_size = '20sp'
        self.size_hint = (None, None)
        self.size = (140, 140)
        self.background_color = background_color
        self.background_normal = ''  # Allow background_color to take effect

        if on_press_callback:
            self.bind(on_press=lambda instance: on_press_callback())


#
# class CircularButton(ButtonBehavior, FloatLayout):
#     def __init__(self, text='', background_color=(0.3, 0.6, 1, 1), on_press_callback=None, **kwargs):
#         super().__init__(**kwargs)
#
#         self.background_color = background_color
#         self.on_press_callback = on_press_callback
#         self.size_hint = (None, None)
#         self.size = (140, 140)
#
#         # Add label (child of FloatLayout — now layout handles sizing)
#         self.label = Label(
#             text=text,
#             color=(1, 1, 1, 1),
#             font_size=20,
#             halign='center',
#             valign='middle',
#             size_hint=(1, 1),
#             text_size=(140, 140),  # Matches button size
#             pos_hint={'center_x': 0.5, 'center_y': 0.5}
#         )
#         self.add_widget(self.label)
#
#         # Redraw when layout changes
#         self.bind(pos=self._update_canvas, size=self._update_canvas)
#         Clock.schedule_once(self._update_canvas, 0)
#
#     def _update_canvas(self, *args):
#         self.canvas.before.clear()
#         with self.canvas.before:
#             Color(*self.background_color)
#             Ellipse(pos=self.pos, size=self.size)
#
#     def on_press(self):
#         if self.on_press_callback:
#             self.on_press_callback()


class MainScreen(Screen):
    def __init__(self, switch_callback, **kwargs):
        super().__init__(**kwargs)
        self.switch_callback = switch_callback
        layout = BoxLayout(orientation='horizontal')

        clock_box = BoxLayout(size_hint=(0.66, 1))
        self.clock = AnalogClock()
        clock_box.add_widget(self.clock)

        button_box = BoxLayout(orientation='vertical', size_hint=(0.34, 1), spacing=40, padding=20)

        # self.request_btn = CircularButton("Request", background_color=(0.2, 0.6, 1, 1), on_press_callback=self.switch_callback['request'])
        # self.release_btn = CircularButton("Release", background_color=(1, 0.3, 0.3, 1), on_press_callback=self.switch_callback['release'])

        self.going_out_button = StyledSquareButton(
            text="Going Outside",
            background_color=(0.2, 0.6, 1, 1),
            on_press_callback=self.switch_callback['request']
        )
        self.main_layout.add_widget(self.going_out_button)

        top = AnchorLayout()
        bottom = AnchorLayout()
        # top.add_widget(self.request_btn)
        # bottom.add_widget(self.release_btn)

        button_box.add_widget(top)
        button_box.add_widget(bottom)

        layout.add_widget(clock_box)
        layout.add_widget(button_box)
        self.add_widget(layout)

class ReservedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.add_widget(Label(text="BUSY", font_size='64sp', color=(1, 1, 1, 1)))

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class InUseScreen(Screen):
    def __init__(self, done_callback, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0.6, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="IN USE", font_size='64sp', color=(1, 1, 1, 1)))
        done_btn = Button(text="Done", size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.5})
        done_btn.bind(on_press=done_callback)

        layout.add_widget(done_btn)
        self.add_widget(layout)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

# ---------- App ----------

class ClockButtonApp(App):
    def build(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, 1883, 60)
        self.client.loop_start()

        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main", switch_callback={
            "request": self.request_access,
            "release": self.release_access
        }))
        self.sm.add_widget(ReservedScreen(name="busy"))
        self.sm.add_widget(InUseScreen(name="inuse", done_callback=self.release_access))
        self.sm.current = "main"
        return self.sm

    def on_connect(self, client, userdata, flags, rc):
        print("📡 Connected to MQTT broker")
        client.subscribe("site/state")

    def request_access(self, *args):
        print(f"🟢 UI ({DEVICE_ID}) requesting access...")
        self.client.publish("site/request", DEVICE_ID)

    def release_access(self, *args):
        print(f"🔴 UI ({DEVICE_ID}) releasing access...")
        self.client.publish("site/release", DEVICE_ID)

    def on_message(self, client, userdata, msg):
        if msg.topic != "site/state":
            return

        import json
        payload = json.loads(msg.payload.decode())
        occupied_by = payload.get("occupied_by")
        print(f"📥 site/state update: occupied_by = {occupied_by}")

        def switch_to(name):
            Clock.schedule_once(lambda dt: setattr(self.sm, "current", name), 0)

        if occupied_by is None:
            switch_to("main")
        elif occupied_by == DEVICE_ID:
            switch_to("inuse")
        else:
            switch_to("busy")

if __name__ == "__main__":
    ClockButtonApp().run()
