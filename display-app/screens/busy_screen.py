from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from datetime import datetime, timezone


class ReservedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images = []
        self.image_index = 0
        self.start_time = None

        self.root_layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        self.label = Label(text="Other dog is outside", font_size='36sp', color=(1, 1, 1, 1), size_hint=(1, 0.2))
        self.image_widget = Image(allow_stretch=True, keep_ratio=True, size_hint=(1, 0.6))
        self.time_label = Label(text="", font_size='20sp', color=(1, 1, 1, 1), size_hint=(1, 0.2))

        self.root_layout.add_widget(self.label)
        self.root_layout.add_widget(self.image_widget)
        self.root_layout.add_widget(self.time_label)
        self.add_widget(self.root_layout)

        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def set_content(self, dog_name, images, theme_color=(1, 0, 0, 1), start_time=None):
        self.label.text = f"{dog_name} is outside"
        self.images = images
        self.image_index = 0
        self.start_time = start_time
        if self.images:
            self.image_widget.source = self.images[0]

        if hasattr(self, "timer_event"):
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

        with self.canvas.before:
            Color(*theme_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_timer(self, dt):
        if not self.start_time:
            self.time_label.text = ""
            return
        try:
            clean_start = self.start_time.replace("Z", "")
            start = datetime.fromisoformat(clean_start)

            now = datetime.now(timezone.utc)
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)

            delta = now - start
            minutes, seconds = divmod(int(delta.total_seconds()), 60)
            self.time_label.text = f"Out for {minutes}m {seconds}s"
            print(f"[⏱️ Timer] {self.name} screen — Start: {start}, Now: {now}, Elapsed: {minutes}m {seconds}s")

        except Exception as e:
            self.time_label.text = ""
            print(f"[⚠️ Timer Error] {self.name} screen:", e)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
