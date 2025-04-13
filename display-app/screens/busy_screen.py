from widgets.dog_status_base import DogStatusScreen


class ReservedScreen(DogStatusScreen):
    def __init__(self, **kwargs):
        super().__init__(
            label_text="Other dog is outside", theme_color=(1, 0, 0, 1), **kwargs
        )
