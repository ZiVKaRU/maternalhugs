# parent_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


class ParentScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "parent"
        # Пока пустой экран — добавь сюда UI позже
        label = MDLabel(text="Окно родителя", halign="center", size_hint_y=None, height=dp(50))
        self.add_widget(label)