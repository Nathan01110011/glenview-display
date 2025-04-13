from widgets.dog_status_base import DogStatusScreen
from widgets.circular_button import CircularButton
from kivy.uix.boxlayout import BoxLayout


class InUseScreen(DogStatusScreen):
    def __init__(self, done_callback, **kwargs):
        super().__init__(
            label_text="You're outside!", theme_color=(0, 0.6, 0, 1), **kwargs
        )
        self.done_callback = done_callback

        # Reconstruct layout for horizontal layout with button
        self.root_layout.clear_widgets()

        self.label.text = "You're outside!"
        self.root_layout.add_widget(self.label)

        main_row = BoxLayout(orientation="horizontal", spacing=40, size_hint=(1, 0.8))

        left_col = BoxLayout(orientation="vertical", spacing=20, size_hint=(0.7, 1))
        left_col.add_widget(self.image_widget)
        left_col.add_widget(self.time_label)

        button_col = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        done_button = CircularButton(
            text="Done",
            background_color=(0.3, 0.3, 0.3, 1),
            on_press_callback=self.done_callback,
        )
        button_col.add_widget(done_button)

        main_row.add_widget(left_col)
        main_row.add_widget(button_col)
        self.root_layout.add_widget(main_row)
