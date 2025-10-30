# main.py
from kid import KidApp
from parent_screen import ParentScreen

# Если хочешь, можешь здесь добавить логику выбора между KidApp и ParentApp
# Но сейчас просто запускаем KidApp

if __name__ == "__main__":
    KidApp().run()