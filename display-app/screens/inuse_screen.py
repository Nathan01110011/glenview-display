from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from widgets.circular_button import CircularButton
from datetime import datetime, timezone


class InUseScreen(Screen):
    def __init__(self, done_callback, **kwargs):
        super().__init__(**kwargs)
        self.done_callback = done_callback
        self.images = []
        self.image_index = 0
        self.start_time = None

        # Layout
        self.root_layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        self.label = Label(text="You're outside!", font_size='36sp', color=(1, 1, 1, 1), size_hint=(1, 0.2))
        self.main_row = BoxLayout(orientation='horizontal', spacing=40, size_hint=(1, 0.8))

        self.left_col = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.7, 1))
        self.image_widget = Image(allow_stretch=True, keep_ratio=True)
        self.time_label = Label(text="", font_size='20sp', color=(1, 1, 1, 1), size_hint=(1, 0.2))

        self.button_col = BoxLayout(orientation='vertical', size_hint=(0.3, 1))
        self.done_button = CircularButton(
            text="Done",
            background_color=(0.3, 0.3, 0.3, 1),
            on_press_callback=self.done_callback
        )

        self.left_col.add_widget(self.image_widget)
        self.left_col.add_widget(self.time_label)
        self.button_col.add_widget(self.done_button)
        self.main_row.add_widget(self.left_col)
        self.main_row.add_widget(self.button_col)

        self.root_layout.add_widget(self.label)
        self.root_layout.add_widget(self.main_row)
        self.add_widget(self.root_layout)

        with self.canvas.before:
            Color(0, 0.6, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def set_content(self, dog_name, images, theme_color=(0, 0.6, 0, 1), start_time=None):
        self.label.text = f"You're outside, {dog_name}!"
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
