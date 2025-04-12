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

        self.label = Label(
            text=text,
            color=(1, 1, 1, 1),
            font_size=20,
            halign='center',
            valign='middle',
            size_hint=(1, 1),
            text_size=(140, 140),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.label)

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
