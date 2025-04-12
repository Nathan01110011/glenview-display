from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'show_cursor', '0')
Config.set('kivy', 'keyboard_mode', 'system')

import os
import math
import httpx
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Line, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import RoundedRectangle

# Config
Window.size = (800, 480)
Window.clearcolor = (0, 0, 0, 1)

DEVICE_ID = os.getenv("DEVICE_ID", "frame2")
SERVER_IP = os.getenv("SERVER_IP", "localhost")
SERVER_URL = f"http://{SERVER_IP}:8000"

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

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock


class CircularButton(ButtonBehavior, FloatLayout):
    def __init__(self, text='', background_color=(0.3, 0.6, 1, 1), on_press_callback=None, **kwargs):
        super().__init__(**kwargs)

        self.background_color = background_color
        self.on_press_callback = on_press_callback
        self.size_hint = (None, None)
        self.size = (140, 140)

        # Add label (child of FloatLayout — now layout handles sizing)
        self.label = Label(
            text=text,
            color=(1, 1, 1, 1),
            font_size=20,
            halign='center',
            valign='middle',
            size_hint=(1, 1),
            text_size=(140, 140),  # Matches button size
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.label)

        # Redraw when layout changes
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        Clock.schedule_once(self._update_canvas, 0)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            Ellipse(pos=self.pos, size=self.size)

    def on_press(self):
        if self.on_press_callback:
            self.on_press_callback()


class MainScreen(Screen):
    def __init__(self, switch_callback, **kwargs):
        super().__init__(**kwargs)
        self.switch_callback = switch_callback

        # Root layout: horizontal split (clock + buttons)
        layout = BoxLayout(orientation='horizontal')

        # Clock + weather stack
        left_column = BoxLayout(orientation='vertical', size_hint=(0.66, 1))

        # Clock (reduced size)
        self.clock = AnalogClock()
        clock_anchor = AnchorLayout(size_hint=(1, 0.7))
        self.clock.size_hint = (None, None)
        self.clock.size = (250, 250)  # Adjust size directly
        clock_anchor.add_widget(self.clock)

        # Weather bar container
        weather_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.3),
            padding=10,
            spacing=15
        )

        # Add background with rounded corners
        with weather_bar.canvas.before:
            Color(0.15, 0.15, 0.15, 0.8)  # Dark translucent gray
            self.weather_bg = RoundedRectangle(radius=[10], pos=weather_bar.pos, size=weather_bar.size)

        # Bind background to layout size/pos
        weather_bar.bind(pos=lambda *a: setattr(self.weather_bg, 'pos', weather_bar.pos))
        weather_bar.bind(size=lambda *a: setattr(self.weather_bg, 'size', weather_bar.size))

        # Weather icon (replace with your actual icon)
        weather_icon = Image(
            source='assets/weather/sun.png',
            size_hint=(None, None),
            size=(48, 48),
            allow_stretch=True
        )
        weather_icon.pos_hint = {'center_y': 0.5}

        # Styled weather text
        temp_label = Label(text='15°C', font_size='22sp', color=(1, 1, 1, 1))
        condition_label = Label(text='Sunny', font_size='22sp', color=(1, 1, 1, 1))
        location_label = Label(text='Glenview', font_size='16sp', color=(0.8, 0.8, 0.8, 1))

        weather_bar.add_widget(weather_icon)
        weather_bar.add_widget(temp_label)
        weather_bar.add_widget(condition_label)
        weather_bar.add_widget(location_label)

        # Buttons column (same as before)
        button_box = BoxLayout(orientation='vertical', size_hint=(0.34, 1), spacing=40, padding=20)
        bottom = AnchorLayout()
        self.going_out_button = CircularButton(
            "Going Outside",
            background_color=(0.2, 0.6, 1, 1),
            on_press_callback=self.switch_callback['request']
        )
        bottom.add_widget(self.going_out_button)
        button_box.add_widget(Widget())  # Empty top space
        button_box.add_widget(bottom)

        layout.add_widget(left_column)
        layout.add_widget(button_box)

        left_column.add_widget(clock_anchor)  # ✅ this adds the clock
        left_column.add_widget(weather_bar)  # ✅ this adds the weather bar

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
        try:
            httpx.post(f"{SERVER_URL}/request", json={"device_id": DEVICE_ID}, timeout=2)
        except Exception as e:
            print("⚠️ Request failed:", e)

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
                elif occupied_by == DEVICE_ID:
                    self.switch_to("inuse")
                else:
                    self.switch_to("busy")
        except Exception as e:
            print("⚠️ Failed to get state:", e)

if __name__ == "__main__":
    ClockButtonApp().run()
