from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

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
