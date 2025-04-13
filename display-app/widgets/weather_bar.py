# display-app/widgets/weather_bar.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import httpx


class WeatherBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, 0.15),
            padding=10,
            spacing=15,
            **kwargs,
        )

        self.failed = False
        self.last_successful = False
        self.last_icon_url = None
        self.server_url = "http://localhost:8000"
        self.bg = None  # Instead of ObjectProperty

        # Background
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.8)
            self.bg = RoundedRectangle(radius=[10], pos=self.pos, size=self.size)
        self._bind_background()

        # Widgets
        self.icon = AsyncImage(
            source="", size_hint=(None, None), size=(48, 48), allow_stretch=True
        )
        self.icon.pos_hint = {"center_y": 0.5}

        self.temp_label = Label(text="--°C", font_size="22sp", color=(1, 1, 1, 1))
        self.condition_label = Label(
            text="Loading...", font_size="22sp", color=(1, 1, 1, 1)
        )
        self.location_label = Label(text="", font_size="16sp", color=(0.8, 0.8, 0.8, 1))

        self.add_widget(self.icon)
        self.add_widget(self.temp_label)
        self.add_widget(self.condition_label)
        self.add_widget(self.location_label)

        Clock.schedule_once(self.update_weather, 0)
        Clock.schedule_interval(self.update_weather, 600)

    def _bind_background(self):
        def update_bg(*_):
            self.bg.pos = self.pos
            self.bg.size = self.size

        self.bind(pos=update_bg, size=update_bg)  # pylint: disable=no-member

    def set_server_url(self, base_url):
        self.server_url = base_url

    def retry_weather_if_needed(self, new_url):
        if self.failed and not self.last_successful:
            self.server_url = new_url
            self.update_weather()

    def update_weather(self, *_):
        try:
            r = httpx.get(f"{self.server_url}/weather", timeout=5)
            r.raise_for_status()
            data = r.json()

            self.temp_label.text = f"{data['temp_c']}°C"
            self.condition_label.text = data["condition"]
            self.location_label.text = data["location"]

            if data["icon_url"] != self.last_icon_url:
                self.icon.source = data["icon_url"]
                self.icon.reload()
                self.last_icon_url = data["icon_url"]

            self.failed = False
            self.last_successful = True

        except httpx.RequestError as e:
            print("⚠️ Weather fetch error:", e)
            self.failed = True
