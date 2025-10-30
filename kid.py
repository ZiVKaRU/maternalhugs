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


KV = '''
MDScreen:

    Image:
        source: 'background.jpg'
        allow_stretch: True
        keep_ratio: False

    MDFloatLayout:

        MDCard:
            id: top_card
            size_hint_x: 0.9
            size_hint_y: None
            height: dp(70)
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
                    spacing: dp(20)

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

        MDIconButton:
            id: prev_month_btn
            icon: 'arrow-left'
            pos_hint: {'center_x': 0.25, 'center_y': 0.7}
            on_release: app.change_month(-1)

        MDIconButton:
            id: next_month_btn
            icon: 'arrow-right'
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
        self.size = (dp(40), dp(40))

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


class KidApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "LightBlue"
        self.today = date.today()
        self.current_date = self.today
        self.current_view = 'month'
        self.lessons = [
            self.today + timedelta(days=5),
            self.today + timedelta(days=12),
            self.today + timedelta(days=19),
        ]

        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(ParentScreen())
        self.main_screen = self.create_main_screen()
        sm.add_widget(self.main_screen)

        users = load_users()
        for email, data in users.items():
            if "session_token" in data:
                user_type = data.get("type", "main")
                self.set_user(email)
                sm.current = user_type
                return sm

        sm.current = "login"
        return sm

    def create_main_screen(self):
        screen = Builder.load_string(KV)
        screen.name = "main"
        top_bar = screen.ids.top_bar

        # Заменяем иконки на фото
        icons = ["map.png", "book-open-variant.png", "star.png", "cog.png"]
        callbacks = [lambda: print("Карта"), lambda: print("Занятия"), lambda: print("Избранное"), lambda: self.open_settings()]

        for icon, callback in zip(icons, callbacks):
            btn = ImageButton(source=icon, callback=callback)
            top_bar.add_widget(btn)

        self.update_switch_buttons(screen)
        self.create_calendar(screen.ids.calendar_grid)
        return screen

    def set_user(self, email):
        self.current_user = email

    def get_current_month_year(self):
        return self.current_date.strftime("%B %Y").capitalize()

    def change_month(self, direction):
        import calendar
        current = self.current_date
        if direction == -1:
            if current.month == 1:
                new_year = current.year - 1
                new_month = 12
            else:
                new_year = current.year
                new_month = current.month - 1
        elif direction == 1:
            if current.month == 12:
                new_year = current.year + 1
                new_month = 1
            else:
                new_year = current.year
                new_month = current.month + 1

        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(current.day, max_day)

        self.current_date = current.replace(year=new_year, month=new_month, day=new_day)

        self.create_calendar(self.main_screen.ids.calendar_grid)
        self.main_screen.ids.month_label.text = self.get_current_month_year()

    def open_settings(self):
        def change_theme():
            if self.theme_cls.theme_style == "Light":
                self.theme_cls.theme_style = "Dark"
            else:
                self.theme_cls.theme_style = "Light"
            self.create_calendar(self.main_screen.ids.calendar_grid)
            self.update_switch_buttons(self.main_screen)
            self.dialog.dismiss()

        theme_text = "Включить тёмный режим?" if self.theme_cls.theme_style == "Light" else "Включить светлый режим?"
        self.dialog = MDDialog(
            title="Настройки",
            text=theme_text,
            buttons=[
                MDRaisedButton(text="ДА", on_release=lambda x: change_theme()),
                MDRaisedButton(text="НЕТ", on_release=lambda x: self.dialog.dismiss()),
            ],
        )
        self.dialog.open()

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
            is_lesson = current_day in self.lessons
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
            is_lesson = current_day in self.lessons
            btn = CalendarDayButton(day_num=day_num, is_today=is_today, is_lesson=is_lesson)
            grid.add_widget(btn)


KidApp().run()