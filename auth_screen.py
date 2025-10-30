# auth_screen.py
import json
import os
import hashlib
import secrets
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App


def get_users_path():
    return os.path.join(App.get_running_app().user_data_dir, "users.json")


def load_users():
    path = get_users_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    path = get_users_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def hash_password(password, salt="kivy_salt_2025"):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def generate_session_token():
    return secrets.token_hex(32)


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="Вход", halign="center", font_style="H5", size_hint_y=None, height=dp(50)))

        self.email = MDTextField(hint_text="Email", mode="rectangle")
        self.password = MDTextField(hint_text="Пароль", password=True, mode="rectangle")
        self.error_label = MDLabel(text="", theme_text_color="Error", halign="center", size_hint_y=None, height=dp(30))

        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(self.error_label)

        btn_login = MDRaisedButton(text="Войти", size_hint_x=None, width=dp(200), pos_hint={"center_x": 0.5})
        btn_login.bind(on_release=self.login)
        layout.add_widget(btn_login)

        btn_to_register = MDRaisedButton(
            text="Нет аккаунта? Зарегистрироваться",
            size_hint_x=None,
            width=dp(250),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        btn_to_register.bind(on_release=lambda x: setattr(MDApp.get_running_app().root, 'current', 'register'))
        layout.add_widget(btn_to_register)

        self.add_widget(layout)

    def login(self, instance):
        email = self.email.text.strip()
        password = self.password.text
        users = load_users()

        if not email or not password:
            self.show_error("Заполните все поля")
            return

        if email not in users:
            self.show_error("Пользователь не найден")
            return

        if users[email]["password"] != hash_password(password):
            self.show_error("Неверный пароль")
            return

        # 🔐 Генерируем и сохраняем токен сессии
        users[email]["session_token"] = generate_session_token()
        save_users(users)

        self.show_error("")
        app = MDApp.get_running_app()
        app.set_user(email)

        # 🔐 Открываем экран в зависимости от типа аккаунта
        user_type = users[email].get("type", "main")  # по умолчанию "main"
        app.root.current = user_type

    def show_error(self, text):
        self.error_label.text = text


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "register"
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="Регистрация", halign="center", font_style="H5", size_hint_y=None, height=dp(50)))

        self.email = MDTextField(hint_text="Email", mode="rectangle")
        self.password = MDTextField(hint_text="Пароль", password=True, mode="rectangle")
        self.password2 = MDTextField(hint_text="Повторите пароль", password=True, mode="rectangle")

        # Выбор типа аккаунта
        type_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        type_label = MDLabel(text="Тип аккаунта:", halign="center", size_hint_x=0.5)

        # Кнопка с выпадающим списком
        self.type_button = MDRaisedButton(
            text="Выбрать",
            size_hint_x=0.5,
            on_release=self.open_dropdown
        )
        type_layout.add_widget(type_label)
        type_layout.add_widget(self.type_button)

        self.error_label = MDLabel(text="", theme_text_color="Error", halign="center", size_hint_y=None, height=dp(30))

        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(self.password2)
        layout.add_widget(type_layout)
        layout.add_widget(self.error_label)

        btn_register = MDRaisedButton(text="Зарегистрироваться", size_hint_x=None, width=dp(200), pos_hint={"center_x": 0.5})
        btn_register.bind(on_release=self.register)
        layout.add_widget(btn_register)

        btn_to_login = MDRaisedButton(
            text="Уже есть аккаунт? Войти",
            size_hint_x=None,
            width=dp(200),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        btn_to_login.bind(on_release=lambda x: setattr(MDApp.get_running_app().root, 'current', 'login'))
        layout.add_widget(btn_to_login)

        # Настройка выпадающего списка
        menu_items = [
            {"text": "Ребенок", "on_release": lambda: self.set_type("main")},
            {"text": "Родитель", "on_release": lambda: self.set_type("parent")},
        ]
        self.menu = MDDropdownMenu(
            caller=self.type_button,
            items=menu_items,
            width_mult=4
        )

        self.add_widget(layout)

    def open_dropdown(self, instance):
        self.menu.open()

    def set_type(self, user_type):
        self.user_type = user_type
        self.type_button.text = "Родитель" if user_type == "parent" else "Ребенок"
        self.menu.dismiss()

    def register(self, instance):
        email = self.email.text.strip()
        password = self.password.text
        password2 = self.password2.text

        # Проверка: выбран ли тип аккаунта
        if not hasattr(self, 'user_type') or not self.user_type:
            self.show_error("Выберите тип аккаунта")
            return

        users = load_users()

        if not email or not password or not password2:
            self.show_error("Заполните все поля")
            return

        if "@" not in email or "." not in email:
            self.show_error("Некорректный email")
            return

        if password != password2:
            self.show_error("Пароли не совпадают")
            return

        if len(password) < 6:
            self.show_error("Пароль должен быть не короче 6 символов")
            return

        if email in users:
            self.show_error("Пользователь с таким email уже существует")
            return

        users[email] = {
            "password": hash_password(password),
            "type": self.user_type  # сохраняем тип аккаунта
        }
        save_users(users)

        self.show_error("")
        Clock.schedule_once(lambda dt: setattr(MDApp.get_running_app().root, 'current', 'login'), 1)

    def show_error(self, text):
        self.error_label.text = text