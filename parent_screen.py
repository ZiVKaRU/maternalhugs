from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.carousel import MDCarousel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
import json
import os
import hashlib
from kivy.app import App
def get_lessons_path():
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "lessons.json")
def get_users_path():
    return os.path.join(App.get_running_app().user_data_dir, "users.json")
def load_lessons():
    path = get_lessons_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lessons = json.load(f)
        updated_lessons = []
        for lesson in lessons:
            if 'date' in lesson and 'day_of_week' not in lesson and 'days_of_week' not in lesson:
                updated_lessons.append({
                    'title': lesson.get('title', 'Без названия'),
                    'days_of_week': [lesson['date']]
                })
            elif 'day_of_week' in lesson and 'days_of_week' not in lesson:
                updated_lessons.append({
                    'title': lesson.get('title', 'Без названия'),
                    'days_of_week': [lesson['day_of_week']]
                })
            else:
                updated_lessons.append(lesson)
        return updated_lessons
    return []
def save_lessons(lessons):
    path = get_lessons_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lessons, f, indent=4, ensure_ascii=False)
def get_unique_title(title, days_of_week_list, lessons):
    days_str = "_".join(sorted(days_of_week_list)) if days_of_week_list else ""
    existing_titles = [lesson['title'] for lesson in lessons if "_".join(sorted(lesson.get("days_of_week", []))) == days_str]
    if title not in existing_titles:
        return title
    counter = 1
    new_title = f"({counter}) {title}"
    while new_title in existing_titles:
        counter += 1
        new_title = f"({counter}) {title}"
    return new_title
def hash_password(password, salt="kivy_salt_2025"):
    return hashlib.sha256((password + salt).encode()).hexdigest()
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
class LessonItem(MDBoxLayout):
    def __init__(self, lesson, is_nearest=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(50)
        self.spacing = dp(10)
        self.padding = [dp(10), 0, dp(10), 0]
        if is_nearest:
            circle = MDLabel(
                text="●",
                color=(0, 1, 0, 1),
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                halign="center",
                valign="middle"
            )
            self.add_widget(circle)
        else:
            from kivy.uix.widget import Widget
            self.add_widget(Widget(size_hint_x=None, width=dp(20)))
        days_str = ", ".join(lesson.get("days_of_week", []))
        day_label = MDLabel(
            text=days_str,
            halign="left",
            size_hint_x=0.4
        )
        title_label = MDLabel(
            text=lesson["title"],
            halign="left",
            size_hint_x=0.6
        )
        self.add_widget(day_label)
        self.add_widget(title_label)
class ParentScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "parent"
        self.lessons = load_lessons()
        self.app_ref = None
        self.current_user = None
        Clock.schedule_once(lambda dt: self.build_ui())
    def build_ui(self):
        layout = MDFloatLayout()
        top_card = MDCard(
            id='top_card',
            size_hint_x=0.9,
            size_hint_y=None,
            height=dp(70),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            radius=[20],
            md_bg_color=self.theme_cls.accent_color,
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        top_bar_container = MDFloatLayout(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        top_bar = MDBoxLayout(
            adaptive_size=True,
            size_hint_x=None,
            spacing=dp(20),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        icons = ["map.png", "book-open-variant.png", "account-child.png", "cog.png"]
        callbacks = [
            lambda: self.open_map_screen(),
            lambda: self.open_lessons_menu(),
            lambda: print("Ребёнок"),
            lambda: self.open_settings()
        ]
        for icon, callback in zip(icons, callbacks):
            btn = ImageButton(source=icon, callback=callback)
            top_bar.add_widget(btn)
        top_bar_container.add_widget(top_bar)
        top_card.add_widget(top_bar_container)
        layout.add_widget(top_card)
        carousel = MDCarousel(
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.18}
        )
        for i in range(1, 4):
            screen = MDScreen()
            try:
                img = Image(
                    source=f'photo{i}.jpg',
                    allow_stretch=False,
                    keep_ratio=True,
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )
                screen.add_widget(img)
            except:
                screen.add_widget(MDLabel(text=f"Фото {i}", halign="center"))
            carousel.add_widget(screen)
        layout.add_widget(carousel)
        self.lessons_card = MDCard(
            id='lessons_card',
            size_hint=(0.9, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.57},
            radius=[15],
            md_bg_color=(0.9, 0.9, 0.9, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        lessons_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        lessons_layout.bind(minimum_height=lessons_layout.setter('height'))
        sorted_lessons = sorted(self.lessons, key=lambda x: x.get("days_of_week", [])[0] if x.get("days_of_week") else "")
        if sorted_lessons:
            for lesson in sorted_lessons:
                is_nearest = False
                item = LessonItem(lesson, is_nearest=is_nearest)
                lessons_layout.add_widget(item)
        else:
            lessons_layout.add_widget(MDLabel(text="Нет занятий", halign="center"))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(lessons_layout)
        self.lessons_card.add_widget(scroll)
        layout.add_widget(self.lessons_card)
        self.lessons_menu = self.build_lessons_menu()
        self.lessons_menu.opacity = 0
        self.lessons_menu.disabled = True
        layout.add_widget(self.lessons_menu)
        if self.app_ref:
            self.update_colors()
        layout.add_widget(Image(
            source='foto.png',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            pos_hint={'right': 1, 'y': 0},
            allow_stretch=True,
            keep_ratio=True
        ))
        self.add_widget(layout)
    def open_lessons_menu(self):
        self.lessons_menu.disabled = False
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self.lessons_menu)
    def close_lessons_menu(self):
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *args: setattr(self.lessons_menu, 'disabled', True))
        anim.start(self.lessons_menu)
    def build_lessons_menu(self):
        menu = MDCard(
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            radius=[15],
            md_bg_color=(0.95, 0.95, 0.95, 1),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        main_layout = MDBoxLayout(orientation="horizontal", spacing=dp(15))
        menu.add_widget(main_layout)
        left_panel = MDBoxLayout(orientation="vertical", size_hint_x=0.4, spacing=dp(10))
        left_panel.add_widget(MDLabel(text="Занятия", halign="center", bold=True, font_style="H6"))
        self.lessons_list_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.lessons_list_layout.bind(minimum_height=self.lessons_list_layout.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.lessons_list_layout)
        left_panel.add_widget(scroll)
        btn_create = MDRaisedButton(
            text="+",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0, 0.5, 1, 1),
            on_release=lambda x: self.create_new_lesson()
        )
        left_panel.add_widget(btn_create)
        btn_close = MDRaisedButton(
            text="Закрыть",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0.5, 0.5, 0.5, 1),
            on_release=lambda x: self.close_lessons_menu()
        )
        left_panel.add_widget(btn_close)
        main_layout.add_widget(left_panel)
        right_panel = MDBoxLayout(orientation="vertical", size_hint_x=0.6, spacing=dp(10))
        right_panel.add_widget(MDLabel(text="Редактирование", halign="center", bold=True, font_style="H6"))
        self.title_field = MDTextField(hint_text="Название", size_hint_y=None, height=dp(50))
        right_panel.add_widget(self.title_field)
        self.days_display_field = MDTextField(
            hint_text="Дни недели",
            helper_text="Нажмите для выбора",
            mode="fill",
            size_hint_y=None,
            height=dp(50),
            readonly=True
        )
        original_on_touch_down = self.days_display_field.on_touch_down
        def custom_on_touch_down(touch):
            if self.days_display_field.collide_point(*touch.pos):
                self.open_days_selection_dialog()
                return True
            return original_on_touch_down(touch) if original_on_touch_down else None
        self.days_display_field.on_touch_down = custom_on_touch_down
        right_panel.add_widget(self.days_display_field)
        btn_delete = MDRaisedButton(
            text="Удалить",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(1, 0, 0, 1),
            on_release=lambda x: self.delete_lesson()
        )
        right_panel.add_widget(btn_delete)
        btn_save = MDRaisedButton(
            text="Сохранить",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0, 1, 0, 1),
            on_release=lambda x: self.save_lesson()
        )
        right_panel.add_widget(btn_save)
        main_layout.add_widget(right_panel)
        self.update_lessons_list()
        return menu
    def open_days_selection_dialog(self):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.dialog import MDDialog
        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        current_days_text = self.days_display_field.text
        current_days = [day.strip() for day in current_days_text.split(", ") if day.strip()] if current_days_text else []
        checkboxes = {}
        checkboxes_layout = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        checkboxes_layout.bind(minimum_height=checkboxes_layout.setter('height'))
        for day in days_of_week:
            row_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
            cb = MDCheckbox(size_hint=(None, None), size=(dp(48), dp(48)), active=(day in current_days))
            lbl = MDLabel(text=day, halign="left", valign="middle")
            lbl.bind(texture_size=lbl.setter('size'))
            lbl.size_hint_x = 1
            row_layout.add_widget(cb)
            row_layout.add_widget(lbl)
            checkboxes[day] = cb
            checkboxes_layout.add_widget(row_layout)
        btn_ok = MDRaisedButton(
            text="ОК",
            on_release=lambda x: self.confirm_days_selection(checkboxes)
        )
        btn_cancel = MDRaisedButton(
            text="Отмена",
            on_release=lambda x: self.dialog.dismiss()
        )
        self.dialog = MDDialog(
            title="Выберите дни недели",
            type="custom",
            content_cls=checkboxes_layout,
            buttons=[btn_ok, btn_cancel],
        )
        self.dialog.open()
    def confirm_days_selection(self, checkboxes_dict):
        selected_days = [day for day, checkbox in checkboxes_dict.items() if checkbox.active]
        self.days_display_field.text = ", ".join(selected_days) if selected_days else ""
        self.dialog.dismiss()
    def update_lessons_list(self):
        self.lessons_list_layout.clear_widgets()
        for lesson in self.lessons:
            days_str = ", ".join(lesson.get("days_of_week", []))
            btn = MDRaisedButton(
                text=f"{lesson['title']} ({days_str})",
                size_hint_y=None,
                height=dp(50)
            )
            btn.lesson_data = lesson
            btn.bind(on_release=lambda x: self.select_lesson(x.lesson_data))
            self.lessons_list_layout.add_widget(btn)
    def select_lesson(self, lesson):
        self.selected_lesson = lesson
        self.title_field.text = lesson["title"]
        days_list = lesson.get("days_of_week", [])
        self.days_display_field.text = ", ".join(days_list) if days_list else ""
    def create_new_lesson(self):
        new_lesson = {"title": "Без названия", "days_of_week": []}
        if not new_lesson["days_of_week"]:
             new_lesson["title"] = get_unique_title(new_lesson["title"], new_lesson["days_of_week"], self.lessons)
        self.lessons.append(new_lesson)
        save_lessons(self.lessons)
        self.update_lessons_list()
        self.select_lesson(new_lesson)
    def delete_lesson(self):
        if hasattr(self, 'selected_lesson'):
            self.lessons.remove(self.selected_lesson)
            save_lessons(self.lessons)
            self.update_lessons_list()
            self.title_field.text = ""
            self.days_display_field.text = ""
    def save_lesson(self):
        if hasattr(self, 'selected_lesson'):
            old_title = self.selected_lesson["title"]
            old_days = self.selected_lesson.get("days_of_week", [])
            new_title = self.title_field.text or "Без названия"
            new_days_text = self.days_display_field.text
            new_days = [day.strip() for day in new_days_text.split(", ") if day.strip()] if new_days_text else []
            combined_old = f"{old_title}_{'_'.join(sorted(old_days))}"
            combined_new = f"{new_title}_{'_'.join(sorted(new_days))}"
            if combined_new != combined_old:
                 check_day = new_days[0] if new_days else ""
                 new_title = get_unique_title(new_title, check_day, self.lessons)
            self.selected_lesson["title"] = new_title
            self.selected_lesson["days_of_week"] = new_days
            save_lessons(self.lessons)
            self.update_lessons_list()
            self.select_lesson(self.selected_lesson)
            Clock.schedule_once(lambda dt: self.update_lessons_display())
    def update_lessons_display(self):
        if hasattr(self, 'lessons_card'):
            self.lessons_card.clear_widgets()
            lessons_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            lessons_layout.bind(minimum_height=lessons_layout.setter('height'))
            sorted_lessons = sorted(self.lessons, key=lambda x: x.get("days_of_week", [])[0] if x.get("days_of_week") else "")
            if sorted_lessons:
                for lesson in sorted_lessons:
                    is_nearest = False
                    item = LessonItem(lesson, is_nearest=is_nearest)
                    lessons_layout.add_widget(item)
            else:
                lessons_layout.add_widget(MDLabel(text="Нет занятий", halign="center"))
            scroll = ScrollView(size_hint=(1, 1))
            scroll.add_widget(lessons_layout)
            self.lessons_card.add_widget(scroll)
    def open_settings(self):
        settings_scr = SettingsScreen(parent_screen_instance=self)
        self.app_ref.root.add_widget(settings_scr)
        self.app_ref.root.current = "settings"
    def open_map_screen(self):
        self.app_ref.current_user_type = "parent"
        self.app_ref.root.current = "map"
    def update_colors(self):
        if self.app_ref.theme_cls.theme_style == "Dark":
            self.md_bg_color = (0.1, 0.1, 0.1, 1)
            if hasattr(self, 'lessons_card'):
                self.lessons_card.md_bg_color = (0.2, 0.2, 0.2, 1)
            if hasattr(self, 'lessons_menu'):
                self.lessons_menu.md_bg_color = (0.25, 0.25, 0.25, 1)
        else:
            self.md_bg_color = (1, 1, 1, 1)
            if hasattr(self, 'lessons_card'):
                self.lessons_card.md_bg_color = (0.9, 0.9, 0.9, 1)
            if hasattr(self, 'lessons_menu'):
                self.lessons_menu.md_bg_color = (0.95, 0.95, 0.95, 1)
    def set_app_ref(self, app_ref):
        self.app_ref = app_ref
        if hasattr(self, 'lessons_card'):
            self.update_colors()
class SettingsScreen(MDScreen):
    def __init__(self, parent_screen_instance, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.parent_screen = parent_screen_instance
        self.app_ref = parent_screen_instance.app_ref
        self.current_user = parent_screen_instance.current_user
        self.current_theme = self.app_ref.theme_cls.theme_style
        self.build_ui()
        self.update_colors()
    def build_ui(self):
        self.layout = MDFloatLayout()
        self.back_btn = MDRaisedButton(
            text="Назад",
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'x': 0.02, 'top': 0.98},
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)
        container = MDBoxLayout(orientation="vertical", spacing=dp(30), padding=dp(30), size_hint=(0.8, 0.8))
        container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        title = MDLabel(text="Настройки", halign="center", font_style="H5", size_hint_y=None, height=dp(50))
        container.add_widget(title)
        theme_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(20))
        self.theme_label = MDLabel(text="Тема:", halign="left", valign="middle", size_hint_x=0.3)
        theme_layout.add_widget(self.theme_label)
        self.theme_button = MDRaisedButton(
            text="Тёмный" if self.current_theme == "Dark" else "Светлый",
            size_hint_x=0.3,
            on_release=self.toggle_theme
        )
        theme_layout.add_widget(self.theme_button)
        container.add_widget(theme_layout)
        separator = MDLabel(height=dp(20))
        container.add_widget(separator)
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
        if self.current_theme == "Dark":
            self.current_theme = "Light"
            self.app_ref.theme_cls.theme_style = "Light"
        else:
            self.current_theme = "Dark"
            self.app_ref.theme_cls.theme_style = "Dark"
        self.theme_button.text = "Тёмный" if self.current_theme == "Dark" else "Светлый"
        self.update_colors()
        self.parent_screen.update_colors()
    def update_colors(self):
        if self.app_ref.theme_cls.theme_style == "Dark":
            self.layout.md_bg_color = (0.1, 0.1, 0.1, 1)
            self.back_btn.md_bg_color = (0.3, 0.3, 0.3, 1)
        else:
            self.layout.md_bg_color = (1, 1, 1, 1)
            self.back_btn.md_bg_color = (0.8, 0.8, 0.8, 1)
    def check_and_logout(self, instance):
        password = self.password_field.text
        if not password:
            print("Пароль не введён")
            return
        users_path = get_users_path()
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = {}
        user_data = users.get(self.current_user)
        if not user_data:
            print("Ошибка: пользователь не найден")
            return
        if user_data["password"] != hash_password(password):
            print("Неверный пароль")
            return
        user_data.pop("session_token", None)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        self.app_ref.root.current = "login"
    def go_back(self, instance):
        self.app_ref.root.current = "parent"