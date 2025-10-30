# kid.py
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.carousel import MDCarousel
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager
from datetime import date, timedelta
from auth_screen import LoginScreen, RegisterScreen, load_users
from parent_screen import ParentScreen
from map_screen import MapScreen # Импортируем MapScreen
import json
import os
import hashlib


def get_users_path():
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "users.json")


def hash_password(password, salt="kivy_salt_2025"):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def load_lessons():
    from kivy.app import App
    path = os.path.join(App.get_running_app().user_data_dir, "lessons.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


KV = '''
MDScreen:
    # md_bg_color: 1, 1, 1, 1  # ❌ Убираем жёсткий фон

    MDFloatLayout:

        MDCard:
            id: top_card
            size_hint_x: 0.9
            size_hint_y: None
            height: dp(70)  # увеличили высоту под большие иконки
            pos_hint: {'center_x': 0.5, 'top': 0.98}
            radius: [20,]
            md_bg_color: app.theme_cls.accent_color
            padding: [dp(10), dp(10), dp(10), dp(10)]

            FloatLayout:
                size_hint: 1, 1
                MDBoxLayout:
                    id: top_bar
                    adaptive_size: True
                    size_hint_x: None
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    spacing: dp(20)  # увеличили расстояние между иконками

        FloatLayout:
            size_hint: None, None
            size: dp(200), dp(40)
            pos_hint: {'center_x': 0.5, 'center_y': 0.85}

            MDBoxLayout:
                id: switch_bar
                size_hint: 1, 1
                spacing: dp(10)
                pos_hint: {'center_x': 0.59, 'center_y': 0.1}

                MDRaisedButton:
                    id: month_btn
                    text: "Месяц"
                    on_release: app.switch_view('month')

                MDRaisedButton:
                    id: week_btn
                    text: "Неделя"
                    on_release: app.switch_view('week')

        # === СТРЕЛОЧКИ ДЛЯ СМЕНЫ МЕСЯЦА ===
        MDIconButton:
            id: prev_month_btn
            icon: 'arrow-left'  # можно заменить на фото
            pos_hint: {'center_x': 0.25, 'center_y': 0.7}
            on_release: app.change_month(-1)

        MDIconButton:
            id: next_month_btn
            icon: 'arrow-right'  # можно заменить на фото
            pos_hint: {'center_x': 0.75, 'center_y': 0.7}
            on_release: app.change_month(1)

        MDLabel:
            id: month_label
            text: app.get_current_month_year()
            halign: "center"
            pos_hint: {'center_x': 0.5, 'center_y': 0.7}
            bold: True
            font_size: dp(18)

        MDGridLayout:
            id: calendar_grid
            cols: 7
            size_hint: 0.9, None
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            height: self.minimum_height
            spacing: dp(2)

        MDCarousel:
            id: carousel
            size_hint: 0.8, 0.2
            pos_hint: {'center_x': 0.5, 'center_y': 0.12}

            Screen:
                Image:
                    source: 'photo1.jpg'
                    allow_stretch: False
                    keep_ratio: True
            Screen:
                Image:
                    source: 'photo2.jpg'
                    allow_stretch: False
                    keep_ratio: True
            Screen:
                Image:
                    source: 'photo3.jpg'
                    allow_stretch: False
                    keep_ratio: True
'''


class ImageButton(ButtonBehavior, Image):
    def __init__(self, source, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.callback = callback
        self.allow_stretch = True
        self.keep_ratio = False
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))  # увеличили размер иконок

    def on_release(self):
        if self.callback:
            self.callback()


class CalendarDayButton(ButtonBehavior, MDLabel):
    def __init__(self, day_num, is_today=False, is_lesson=False, **kwargs):
        super().__init__(**kwargs)
        self.day_num = day_num
        self.is_today = is_today
        self.is_lesson = is_lesson
        self.text = str(day_num) if day_num else ""
        self.halign = "center"
        self.valign = "middle"
        self.size_hint = (1, None)
        self.height = dp(40)

        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            default_color = (1, 1, 1, 1)
        else:
            default_color = (0, 0, 0, 1)

        if is_today:
            self.color = (0, 0.75, 1, 1)
        elif is_lesson:
            self.color = (0, 0, 1, 1)
        else:
            self.color = default_color

    def on_release(self):
        pass


# --- Начало: Копируем SettingsScreen из parent_screen.py ---
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

class SettingsScreen(MDScreen):
    def __init__(self, parent_app_instance, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.parent_app = parent_app_instance
        self.app_ref = parent_app_instance
        self.current_user = parent_app_instance.current_user
        self.current_theme = self.app_ref.theme_cls.theme_style
        self.build_ui()
        # Убедимся, что цвета установлены правильно при создании
        self.update_colors()

    def build_ui(self):
        self.layout = MDFloatLayout() # Сохраняем ссылку на основной макет

        # Кнопка "Назад"
        self.back_btn = MDRaisedButton(
            text="Назад",
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'x': 0.02, 'top': 0.98},
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)

        # Основной контейнер
        container = MDBoxLayout(orientation="vertical", spacing=dp(30), padding=dp(30), size_hint=(0.8, 0.8))
        container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Заголовок
        title = MDLabel(text="Настройки", halign="center", font_style="H5", size_hint_y=None, height=dp(50))
        container.add_widget(title)

        # Тема - используем MDBoxLayout для горизонтального размещения
        theme_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(20))

        # Левая часть - надпись "Тема:"
        self.theme_label = MDLabel(text="Тема:", halign="left", valign="middle", size_hint_x=0.3)
        theme_layout.add_widget(self.theme_label)

        # Центральная часть - кнопка переключения темы
        self.theme_button = MDRaisedButton(
            text="Тёмный" if self.current_theme == "Dark" else "Светлый",
            size_hint_x=0.3,
            on_release=self.toggle_theme
        )
        theme_layout.add_widget(self.theme_button)

        # Добавляем горизонтальный макет в основной контейнер
        container.add_widget(theme_layout)

        # Разделитель
        separator = MDLabel(height=dp(20))
        container.add_widget(separator)

        # Выход из аккаунта
        logout_label = MDLabel(text="Выход из аккаунта", halign="center", font_style="H6", size_hint_y=None, height=dp(50))
        container.add_widget(logout_label)

        password_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))

        self.password_field = MDTextField(
            hint_text="Пароль",
            password=True,
            size_hint_x=0.7
        )
        password_layout.add_widget(self.password_field)

        submit_btn = MDRaisedButton(
            text="|>",
            size_hint_x=0.2,
            on_release=self.check_and_logout
        )
        password_layout.add_widget(submit_btn)

        container.add_widget(password_layout)

        self.layout.add_widget(container)
        self.add_widget(self.layout)

    def toggle_theme(self, instance):
        # Переключаем тему
        if self.current_theme == "Dark":
            self.current_theme = "Light"
            self.app_ref.theme_cls.theme_style = "Light"
        else:
            self.current_theme = "Dark"
            self.app_ref.theme_cls.theme_style = "Dark"

        # Обновляем текст кнопки
        self.theme_button.text = "Тёмный" if self.current_theme == "Dark" else "Светлый"

        # Обновляем цвета
        self.update_colors()
        # Обновляем цвета в родительском окне при возврате
        # Для окна ребёнка обновляем цвета самого окна
        self.parent_app.set_background_color()
        # Также обновляем цвета в календаре и других элементах
        self.parent_app.update_switch_buttons(self.parent_app.main_screen)
        self.parent_app.create_calendar(self.parent_app.main_screen.ids.calendar_grid)

    def update_colors(self):
        # Обновляем цвета в зависимости от темы
        if self.app_ref.theme_cls.theme_style == "Dark":
            # Тёмная тема
            self.layout.md_bg_color = (0.1, 0.1, 0.1, 1)  # тёмный фон
            self.back_btn.md_bg_color = (0.3, 0.3, 0.3, 1) # серый фон кнопки
            # Цвет текста для MDLabel по умолчанию обычно корректный для темы
        else:
            # Светлая тема
            self.layout.md_bg_color = (1, 1, 1, 1)  # белый фон
            self.back_btn.md_bg_color = (0.8, 0.8, 0.8, 1) # светло-серый фон кнопки

    def check_and_logout(self, instance):
        password = self.password_field.text
        if not password:
            print("Пароль не введён")
            return

        # Загружаем данные пользователя
        users_path = get_users_path()
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = {}

        # --- Проверяем, является ли текущий пользователь ребёнком ---
        current_user_data = users.get(self.current_user)
        if not current_user_data:  # <--- Вот тут была ошибка
            print("Ошибка: пользователь не найден")
            return

        if current_user_data.get("type") == "main": # Если текущий - ребёнок
            # Ищем родительский аккаунт
            parent_email = None
            for email, data in users.items():
                if data.get("type") == "parent":
                    parent_email = email
                    break

            if not parent_email:
                print("Ошибка: родительский аккаунт не найден для проверки пароля")
                return

            # Сравниваем введённый пароль с паролем родителя
            if users[parent_email]["password"] != hash_password(password):
                print("Неверный пароль родителя")
                return
        else: # Если текущий - родитель
            if current_user_data["password"] != hash_password(password):
                print("Неверный пароль")
                return

        # Удаляем сессию текущего пользователя
        current_user_data.pop("session_token", None)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

        # Переходим на экран входа
        self.app_ref.root.current = "login"

    def go_back(self, instance):
        self.app_ref.root.current = "main"
# --- Конец: Копируем SettingsScreen из parent_screen.py ---


class KidApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "LightBlue"
        self.today = date.today()
        self.current_date = self.today
        self.current_view = 'month'
        self.lessons = load_lessons() # Загружаем из файла
        # Фильтруем занятия, оставляя только те, что с типом 'date' (для совместимости)
        # или преобразуем все в формат 'date' при загрузке
        # Для простоты, оставим как есть, если формат совпадает
        # Иначе, см. load_lessons в parent_screen.py

        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())

        # Сначала создаём и настраиваем ParentScreen
        parent_scr = ParentScreen()
        parent_scr.set_app_ref(self)  # ✅ Передаём ссылку на app
        sm.add_widget(parent_scr)

        # Затем создаём и добавляем MapScreen
        map_scr = MapScreen(parent_app_instance=self) # Создаём экземпляр MapScreen
        sm.add_widget(map_scr) # Добавляем его

        self.main_screen = self.create_main_screen()
        sm.add_widget(self.main_screen)

        # 🔐 Проверка сессии при запуске
        users = load_users()
        for email, data in users.items():
            if "session_token" in data:
                # 🔐 Открываем экран в зависимости от типа аккаунта
                user_type = data.get("type", "main")
                self.set_user(email) # Устанавливаем current_user и передаём его в ParentScreen
                if user_type == "parent":
                    parent_scr.current_user = email
                sm.current = user_type  # "main" или "parent"
                return sm

        sm.current = "login"
        return sm

    def on_start(self):
        # Устанавливаем цвет фона при запуске
        self.set_background_color()

    def set_background_color(self):
        # Устанавливаем цвет фона в зависимости от темы
        if self.theme_cls.theme_style == "Dark":
            self.main_screen.md_bg_color = (0.1, 0.1, 0.1, 1)  # тёмно-серый
        else:
            self.main_screen.md_bg_color = (1, 1, 1, 1)  # белый

    def create_main_screen(self):
        screen = Builder.load_string(KV)
        screen.name = "main"  # ✅ Убедимся, что экран имеет имя "main"
        top_bar = screen.ids.top_bar

        # Заменяем иконки на фото
        icons = ["map.png", "book-open-variant.png", "star.png", "cog.png"]
        callbacks = [lambda: self.open_map_screen(), lambda: print("Занятия"), lambda: print("Избранное"), lambda: self.open_settings()] # Изменили "Карта"

        for icon, callback in zip(icons, callbacks):
            btn = ImageButton(source=icon, callback=callback)
            top_bar.add_widget(btn)

        self.update_switch_buttons(screen)
        self.create_calendar(screen.ids.calendar_grid)
        return screen

    def set_user(self, email):
        self.current_user = email
        # Добавим тип пользователя для экрана карты
        users = load_users()
        self.current_user_type = users.get(email, {}).get("type", "main")

    def get_current_month_year(self):
        # Возвращает строку "Месяц Год" (например, "Октябрь 2025")
        return self.current_date.strftime("%B %Y").capitalize()

    def change_month(self, direction):
        # direction: -1 (назад), +1 (вперёд)
        import calendar
        current = self.current_date
        if direction == -1:
            # Перейти на один месяц назад
            if current.month == 1:
                new_year = current.year - 1
                new_month = 12
            else:
                new_year = current.year
                new_month = current.month - 1
        elif direction == 1:
            # Перейти на один месяц вперёд
            if current.month == 12:
                new_year = current.year + 1
                new_month = 12
            else:
                new_year = current.year
                new_month = current.month + 1

        # Получаем количество дней в новом месяце
        max_day = calendar.monthrange(new_year, new_month)[1]
        # Используем min, чтобы не выйти за пределы
        new_day = min(current.day, max_day)

        self.current_date = current.replace(year=new_year, month=new_month, day=new_day)

        # Обновить календарь и месяц на экране
        self.create_calendar(self.main_screen.ids.calendar_grid)
        self.main_screen.ids.month_label.text = self.get_current_month_year()

    def open_settings(self):
        # Создаём новый экран настроек и добавляем его в ScreenManager
        settings_scr = SettingsScreen(parent_app_instance=self)
        self.root.add_widget(settings_scr)
        self.root.current = "settings"

    def open_map_screen(self):
        # Устанавливаем тип текущего пользователя (для возврата)
        self.current_user_type = "main"
        self.root.current = "map"

    def update_switch_buttons(self, screen):
        month_btn = screen.ids.month_btn
        week_btn = screen.ids.week_btn

        if self.theme_cls.theme_style == "Dark":
            text_color = (1, 1, 1, 1)
            inactive_color = (0.2, 0.2, 0.2, 1)
        else:
            text_color = (0, 0, 0, 1)
            inactive_color = (0.95, 0.95, 0.95, 1)

        month_btn.text_color = text_color
        week_btn.text_color = text_color

        primary = self.theme_cls.primary_color
        if self.current_view == 'month':
            month_btn.md_bg_color = primary
            week_btn.md_bg_color = inactive_color
        else:
            week_btn.md_bg_color = primary
            month_btn.md_bg_color = inactive_color

    def switch_view(self, view):
        self.current_view = view
        self.update_switch_buttons(self.main_screen)
        self.create_calendar(self.main_screen.ids.calendar_grid)

    def create_calendar(self, grid):
        grid.clear_widgets()
        if self.current_view == 'month':
            self.create_month_calendar(grid)
        else:
            self.create_week_calendar(grid)

    def create_month_calendar(self, grid):
        week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day in week_days:
            lbl = MDLabel(text=day, halign="center", size_hint_y=None, height=dp(40), bold=True)
            grid.add_widget(lbl)

        first = self.current_date.replace(day=1)
        start_day = first - timedelta(days=first.weekday())
        for i in range(42):
            current_day = start_day + timedelta(days=i)
            day_num = current_day.day if current_day.month == self.current_date.month else None
            is_today = current_day == self.today
            # Проверяем, есть ли занятие в этот день (по дате)
            is_lesson = any(lesson.get('date') == current_day.strftime("%Y-%m-%d") for lesson in self.lessons)
            btn = CalendarDayButton(day_num=day_num, is_today=is_today, is_lesson=is_lesson)
            grid.add_widget(btn)

    def create_week_calendar(self, grid):
        week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day in week_days:
            lbl = MDLabel(text=day, halign="center", size_hint_y=None, height=dp(40), bold=True)
            grid.add_widget(lbl)

        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            day_num = current_day.day
            is_today = current_day == self.today
            # Проверяем, есть ли занятие в этот день (по дате)
            is_lesson = any(lesson.get('date') == current_day.strftime("%Y-%m-%d") for lesson in self.lessons)
            btn = CalendarDayButton(day_num=day_num, is_today=is_today, is_lesson=is_lesson)
            grid.add_widget(btn)


KidApp().run()