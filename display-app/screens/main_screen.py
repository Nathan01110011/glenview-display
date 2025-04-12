from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from widgets.analog_clock import AnalogClock
from widgets.circular_button import CircularButton
import httpx

SERVER_URL = "http://localhost:8000"

class MainScreen(Screen):
    last_icon_url = None
    def __init__(self, switch_callback, **kwargs):
        super().__init__(**kwargs)
        self.switch_callback = switch_callback

        layout = BoxLayout(orientation='vertical')

        # Top server status bar
        self.status_bar = Label(
            text="Server Offline",
            font_size='16sp',
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1)
        )
        self.status_bar.canvas.before.clear()
        with self.status_bar.canvas.before:
            Color(1, 0.2, 0.2, 1)
            self.status_bg = RoundedRectangle(radius=[0], pos=self.status_bar.pos, size=self.status_bar.size)
        self.status_bar.bind(pos=lambda *a: setattr(self.status_bg, 'pos', self.status_bar.pos))
        self.status_bar.bind(size=lambda *a: setattr(self.status_bg, 'size', self.status_bar.size))

        content_layout = BoxLayout(orientation='horizontal')

        left_column = BoxLayout(orientation='vertical', size_hint=(0.66, 1))

        self.clock = AnalogClock()
        clock_anchor = AnchorLayout(size_hint=(1, 0.7))
        self.clock.size_hint = (None, None)
        self.clock.size = (250, 250)
        clock_anchor.add_widget(self.clock)

        self.weather_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), padding=10, spacing=15)
        with self.weather_bar.canvas.before:
            Color(0.15, 0.15, 0.15, 0.8)
            self.weather_bg = RoundedRectangle(radius=[10], pos=self.weather_bar.pos, size=self.weather_bar.size)
        self.weather_bar.bind(pos=lambda *a: setattr(self.weather_bg, 'pos', self.weather_bar.pos))
        self.weather_bar.bind(size=lambda *a: setattr(self.weather_bg, 'size', self.weather_bar.size))

        self.weather_icon = AsyncImage(source='', size_hint=(None, None), size=(48, 48), allow_stretch=True)
        self.weather_icon.pos_hint = {'center_y': 0.5}
        self.temp_label = Label(text='--°C', font_size='22sp', color=(1, 1, 1, 1))
        self.condition_label = Label(text='Loading...', font_size='22sp', color=(1, 1, 1, 1))
        self.location_label = Label(text='', font_size='16sp', color=(0.8, 0.8, 0.8, 1))

        self.weather_bar.add_widget(self.weather_icon)
        self.weather_bar.add_widget(self.temp_label)
        self.weather_bar.add_widget(self.condition_label)
        self.weather_bar.add_widget(self.location_label)

        left_column.add_widget(clock_anchor)
        left_column.add_widget(self.weather_bar)

        button_box = BoxLayout(orientation='vertical', size_hint=(0.34, 1), spacing=40, padding=20)
        bottom = AnchorLayout()
        self.going_out_button = CircularButton(
            "Going Outside",
            background_color=(0.2, 0.6, 1, 1),
            on_press_callback=self.switch_callback['request']
        )
        bottom.add_widget(self.going_out_button)
        button_box.add_widget(Label())  # Spacer
        button_box.add_widget(bottom)

        content_layout.add_widget(left_column)
        content_layout.add_widget(button_box)

        layout.add_widget(self.status_bar)
        layout.add_widget(content_layout)
        self.add_widget(layout)

        Clock.schedule_once(self.update_weather, 0)
        Clock.schedule_interval(self.update_weather, 600)
        Clock.schedule_interval(self.check_server_status, 5)

    def show_requesting_state(self):
        self.going_out_button.label.text = "Requesting..."
        self.going_out_button.disabled = True

    def reset_request_button(self):
        self.going_out_button.label.text = "Going Outside"
        self.going_out_button.disabled = False

    def update_weather(self, dt):
        try:
            r = httpx.get(f"{SERVER_URL}/weather", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.temp_label.text = f"{data['temp_c']}°C"
                self.condition_label.text = data['condition']
                self.location_label.text = data['location']
                if data['icon_url'] != self.last_icon_url:
                    self.weather_icon.source = data['icon_url']
                    self.weather_icon.reload()
                    self.last_icon_url = data['icon_url']
        except Exception as e:
            print("⚠️ Failed to update weather widget:", e)

    def check_server_status(self, dt):
        try:
            r = httpx.get(f"{SERVER_URL}/state", timeout=3)
            if r.status_code == 200:
                self.status_bar.opacity = 0
                self.going_out_button.disabled = False
                self.update_weather(0)  # Immediately refresh weather now that server is back
        except Exception:
            self.status_bar.opacity = 1
            self.going_out_button.disabled = True