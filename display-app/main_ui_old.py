from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'show_cursor', '0')
Config.set('kivy', 'keyboard_mode', 'dock')

import os
import math
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Ellipse, Rectangle

import paho.mqtt.client as mqtt

DEVICE_ID = os.environ.get("DEVICE_ID", "frame1")
BROKER_IP = os.environ.get("BROKER_IP", "localhost")

Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)


class AnalogClock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 1)
        self.bind(pos=self.update_clock, size=self.update_clock)

    def update_clock(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            center_x, center_y = self.center
            radius = min(self.width, self.height) / 2.2
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

            now = datetime.now()
            sec_angle = math.radians((now.second / 60) * 360)
            min_angle = math.radians((now.minute / 60) * 360)
            hour_angle = math.radians(((now.hour % 12 + now.minute / 60) / 12) * 360)

            Color(0, 0, 0)
            self.draw_hand(center_x, center_y, radius * 0.5, hour_angle, 4)
            self.draw_hand(center_x, center_y, radius * 0.7, min_angle, 3)
            Color(1, 0, 0)
            self.draw_hand(center_x, center_y, radius * 0.9, sec_angle, 2)

    def draw_hand(self, cx, cy, length, angle, width):
        from kivy.graphics import Line
        Line(points=[cx, cy, cx + length * math.sin(angle), cy + length * math.cos(angle)], width=width)


class CircularButton(ButtonBehavior, Widget):
    def __init__(self, text='', background_color=(0.3, 0.6, 1, 1), on_press_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.background_color = background_color
        self.on_press_callback = on_press_callback
        self.size_hint = (None, None)
        self.size = (140, 140)
        Clock.schedule_once(self._init_draw, 0)

    def _init_draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.background_color)
            Ellipse(pos=self.pos, size=self.size)
        if not hasattr(self, 'label'):
            self.label = Label(text=self.text, color=(1, 1, 1, 1), font_size=20, halign='center', valign='middle')
            self.add_widget(self.label)
        self.label.center = self.center

    def on_size(self, *args):
        self._init_draw()

    def on_pos(self, *args):
        self._init_draw()

    def on_press(self):
        if self.on_press_callback:
            self.on_press_callback()


class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='horizontal')

        clock_container = BoxLayout(size_hint=(0.66, 1))
        self.analog_clock = AnalogClock()
        clock_container.add_widget(self.analog_clock)
        layout.add_widget(clock_container)

        button_area = BoxLayout(orientation='vertical', size_hint=(0.34, 1), spacing=40, padding=20)
        top_button = AnchorLayout()
        bottom_button = AnchorLayout()

        self.request_button = CircularButton(
            text='Request', background_color=(0.2, 0.6, 1, 1),
            on_press_callback=self.send_request
        )
        self.release_button = CircularButton(
            text='Release', background_color=(1, 0.3, 0.3, 1),
            on_press_callback=self.send_release
        )

        top_button.add_widget(self.request_button)
        bottom_button.add_widget(self.release_button)

        button_area.add_widget(top_button)
        button_area.add_widget(bottom_button)

        layout.add_widget(button_area)
        self.add_widget(layout)

    def send_request(self):
        print(f"🟢 UI ({DEVICE_ID}) requesting access...")
        self.app.client.publish("site/request", DEVICE_ID)

    def send_release(self):
        print(f"🔴 UI ({DEVICE_ID}) releasing access...")
        self.app.client.publish("site/release", DEVICE_ID)


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
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(0, 0.6, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        layout.add_widget(Label(text="IN USE", font_size='64sp', color=(1, 1, 1, 1)))
        done_button = Button(text="Done", size_hint=(None, None), size=(200, 100),
                             pos_hint={'center_x': 0.5}, on_press=self.release)
        layout.add_widget(done_button)
        self.add_widget(layout)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def release(self, *args):
        self.app.client.publish("site/release", DEVICE_ID)
        self.manager.current = 'main'


class ClockButtonApp(App):
    def build(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, 1883, 60)
        self.client.loop_start()

        self.sm = ScreenManager()
        self.main_screen = MainScreen(app=self, name='main')
        self.inuse_screen = InUseScreen(app=self, name='inuse')
        self.reserved_screen = ReservedScreen(name='reserved')
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.inuse_screen)
        self.sm.add_widget(self.reserved_screen)

        return self.sm

    def on_connect(self, client, userdata, flags, rc):
        print("📡 Connected to MQTT broker.")
        client.subscribe("site/state")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        print(f"📥 Received state update: {payload}")
        if payload == "available":
            self.sm.current = 'main'
        elif payload == DEVICE_ID:
            self.sm.current = 'inuse'
        else:
            self.sm.current = 'reserved'


if __name__ == '__main__':
    ClockButtonApp().run()
