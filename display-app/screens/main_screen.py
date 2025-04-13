from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

from widgets.analog_clock import AnalogClock
from widgets.circular_button import CircularButton
from widgets.weather_bar import WeatherBar
import httpx  # ✅ moved to toplevel


class MainScreen(Screen):
    def __init__(self, switch_callback, **kwargs):
        super().__init__(**kwargs)
        self.switch_callback = switch_callback

        layout = BoxLayout(orientation="vertical")

        # 🔧 Status bar with background
        self.status_bar = Label(
            text="Server Offline",
            font_size="16sp",
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1),
        )

        self.status_bar.canvas.before.clear()
        with self.status_bar.canvas.before:
            Color(1, 0.2, 0.2, 1)
            self.status_bg = RoundedRectangle(
                radius=[0], pos=self.status_bar.pos, size=self.status_bar.size
            )

        # ✅ Use lambda safely (pylint false positive fix)
        (self.status_bar).bind(
            pos=lambda *a: setattr(self.status_bg, "pos", self.status_bar.pos)
        )
        (self.status_bar).bind(
            size=lambda *a: setattr(self.status_bg, "size", self.status_bar.size)
        )

        # Layout blocks
        content_layout = BoxLayout(orientation="horizontal")
        left_column = BoxLayout(orientation="vertical", size_hint=(0.66, 1))

        # Analog Clock
        self.clock = AnalogClock()
        clock_anchor = AnchorLayout(size_hint=(1, 0.7))
        self.clock.size_hint = (None, None)
        self.clock.size = (250, 250)
        clock_anchor.add_widget(self.clock)

        # Weather bar widget
        self.weather_bar = WeatherBar()

        left_column.add_widget(clock_anchor)
        left_column.add_widget(self.weather_bar)

        # Request Button
        button_box = BoxLayout(
            orientation="vertical", size_hint=(0.34, 1), spacing=40, padding=20
        )
        bottom = AnchorLayout()
        self.going_out_button = CircularButton(
            "Going Outside",
            background_color=(0.2, 0.6, 1, 1),
            on_press_callback=self.switch_callback["request"],
        )
        bottom.add_widget(self.going_out_button)
        button_box.add_widget(Label())  # Spacer
        button_box.add_widget(bottom)

        content_layout.add_widget(left_column)
        content_layout.add_widget(button_box)

        layout.add_widget(self.status_bar)
        layout.add_widget(content_layout)
        self.add_widget(layout)

        Clock.schedule_interval(self.check_server_status, 5)

    def show_requesting_state(self):
        self.going_out_button.label.text = "Requesting..."
        self.going_out_button.disabled = True

    def reset_request_button(self):
        self.going_out_button.label.text = "Going Outside"
        self.going_out_button.disabled = False

    def check_server_status(self, _dt):
        try:
            response = httpx.get(f"{self.weather_bar.server_url}/state", timeout=3)
            if response.status_code == 200:
                self.status_bar.opacity = 0
                self.going_out_button.disabled = False
                self.weather_bar.update_weather()
        except httpx.RequestError as e:
            print("⚠️ Server status check failed:", e)
            self.status_bar.opacity = 1
            self.going_out_button.disabled = True
