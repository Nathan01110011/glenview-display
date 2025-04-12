from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
import math
from datetime import datetime

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
            hour_angle = self.angle(now.hour % 12 + now.minute / 60, 12)
            min_angle = self.angle(now.minute, 60)
            sec_angle = self.angle(now.second, 60)

            Color(0, 0, 0)
            self.draw_hand(cx, cy, r * 0.5, hour_angle, 4)
            Color(0, 0, 0)
            self.draw_hand(cx, cy, r * 0.7, min_angle, 3)
            Color(1, 0, 0)
            self.draw_hand(cx, cy, r * 0.9, sec_angle, 2)

    def draw_hand(self, cx, cy, length, angle, width):
        Line(points=[cx, cy, cx + length * math.sin(angle), cy + length * math.cos(angle)], width=width)

    def angle(self, value, max_value):
        return math.radians((value / max_value) * 360)