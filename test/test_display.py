from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'show_cursor', '0')
Config.set('kivy', 'keyboard_mode', 'dock')

from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Ellipse, Line
from datetime import datetime
import math

EventLoop.ensure_window()
Window.release_all_keyboards()
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
            Line(points=[center_x, center_y, center_x + radius * 0.5 * math.sin(hour_angle), center_y + radius * 0.5 * math.cos(hour_angle)], width=4)
            Line(points=[center_x, center_y, center_x + radius * 0.7 * math.sin(min_angle), center_y + radius * 0.7 * math.cos(min_angle)], width=3)

            Color(1, 0, 0)
            Line(points=[center_x, center_y, center_x + radius * 0.9 * math.sin(sec_angle), center_y + radius * 0.9 * math.cos(sec_angle)], width=2)

class CircularButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (140, 140)
        self.background_normal = ''
        self.background_color = kwargs.get('background_color', (0.3, 0.6, 1, 1))
        self.font_size = 20
        self.color = (1, 1, 1, 1)

class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)

        # Left 2/3: Analog clock
        clock_container = BoxLayout(size_hint=(0.66, 1))
        self.analog_clock = AnalogClock()
        clock_container.add_widget(self.analog_clock)
        self.add_widget(clock_container)

        # Right 1/3: Buttons stacked vertically
        button_area = BoxLayout(orientation='vertical', size_hint=(0.34, 1), spacing=40, padding=20)

        top_button = AnchorLayout()
        bottom_button = AnchorLayout()

        self.request_button = CircularButton(text='Request', background_color=(0.2, 0.6, 1, 1))
        self.release_button = CircularButton(text='Release', background_color=(1, 0.3, 0.3, 1))

        top_button.add_widget(self.request_button)
        bottom_button.add_widget(self.release_button)

        button_area.add_widget(top_button)
        button_area.add_widget(bottom_button)

        self.add_widget(button_area)

class ClockButtonApp(App):
    def build(self):
        return MainUI()

if __name__ == '__main__':
    ClockButtonApp().run()
