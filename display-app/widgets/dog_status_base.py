"""Shared screen base class for 'in use' and 'busy' dog display views."""

from datetime import datetime, timezone

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle


class DogStatusScreen(Screen):
    """Reusable layout for dog activity display screens."""

    def __init__(self, label_text, theme_color, **kwargs):
        super().__init__(**kwargs)
        self.images = []
        self.image_index = 0
        self.start_time = None
        self.theme_color = theme_color
        self.timer_event = None  # Pre-declared to avoid Pylint error

        # Main layout
        self.root_layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

        self.label = Label(
            text=label_text,
            font_size="36sp",
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
        )
        self.image_widget = Image(
            allow_stretch=True, keep_ratio=True, size_hint=(1, 0.6)
        )
        self.time_label = Label(
            text="",
            font_size="20sp",
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
        )

        self.root_layout.add_widget(self.label)
        self.root_layout.add_widget(self.image_widget)
        self.root_layout.add_widget(self.time_label)
        self.add_widget(self.root_layout)

        with self.canvas.before:
            Color(*self.theme_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)  # pylint: disable=no-member

    def set_content(self, dog_name, images, theme_color=None, start_time=None):
        """Update display with dog info, background color, and start timer."""
        self.label.text = f"{dog_name} is outside"
        self.images = images
        self.image_index = 0
        self.start_time = start_time

        if theme_color:
            self.theme_color = theme_color

        if self.images:
            self.image_widget.source = self.images[0]

        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

        with self.canvas.before:
            Color(*self.theme_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_timer(self, _=None):
        """Update the 'Out for X minutes' label each second."""
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
            print(
                f"[⏱️ Timer] {self.name} screen — Start: {start}, Now: {now}, "
                f"Elapsed: {minutes}m {seconds}s"
            )

        except ValueError as e:
            self.time_label.text = ""
            print(f"[⚠️ Timer Error] {self.name} screen: {e}")

    def _update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos
