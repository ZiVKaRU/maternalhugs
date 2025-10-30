# parent_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.card import MDCard
from map_screen import MapScreen
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

from kivy.app import App  # <--- Добавь ЭТОТ импорт


def get_lessons_path():
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "lessons.json")


def get_users_path():
    print(f"get_users_path возвращает: {os.path.join(App.get_running_app().user_data_dir, 'users.json')}") # Отладка
    return os.path.join(App.get_running_app().user_data_dir, "users.json")


def load_lessons():
    path = get_lessons_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lessons = json.load(f)
        # --- Начало конвертации ---
        updated_lessons = []
        for lesson in lessons:
            if 'date' in lesson and 'day_of_week' not in lesson and 'days_of_week' not in lesson:
                # Если есть 'date' и нет 'day_of_week' или 'days_of_week', создаём новую запись
                updated_lessons.append({
                    'title': lesson.get('title', 'Без названия'),
                    'days_of_week': [lesson['date']] # Помещаем старую дату как один день
                })
            elif 'day_of_week' in lesson and 'days_of_week' not in lesson:
                # Если есть 'day_of_week' и нет 'days_of_week', конвертируем
                updated_lessons.append({
                    'title': lesson.get('title', 'Без названия'),
                    'days_of_week': [lesson['day_of_week']]
                })
            else:
                # Если 'days_of_week' уже есть, оставляем как есть
                updated_lessons.append(lesson)
        # --- Конец конвертации ---
        return updated_lessons
    return []


def save_lessons(lessons):
    path = get_lessons_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lessons, f, indent=4, ensure_ascii=False)


def get_unique_title(title, days_of_week_list, lessons):
    # days_of_week_list - это список дней недели
    # Создаём строку для проверки, например, "Понедельник_Среда"
    days_str = "_".join(sorted(days_of_week_list)) if days_of_week_list else ""
    # Проверяем, есть ли уже занятие с такими днями и названием
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
        self.size = (dp(40), dp(40))  # размер иконка

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

        # Зелёный кружок слева, если ближайшее
        if is_nearest:
            circle = MDLabel(
                text="●",
                color=(0, 1, 0, 1),  # зелёный
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                halign="center",
                valign="middle"
            )
            self.add_widget(circle)
        else:
            # Пустое пространство для выравнивания
            from kivy.uix.widget import Widget
            self.add_widget(Widget(size_hint_x=None, width=dp(20)))

        # Дни недели и название (объединяем дни в строку)
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

    def open_map_screen(self):
        # Устанавливаем тип текущего пользователя (для возврата)
        self.app_ref.current_user_type = "parent"
        self.app_ref.root.current = "map"

    def build_ui(self):
        layout = MDFloatLayout()

        # === Голубая панель сверху ===
        top_card = MDCard(
            id='top_card',
            size_hint_x=0.9,
            size_hint_y=None,
            height=dp(70),  # как у ребёнка
            pos_hint={'center_x': 0.5, 'top': 0.98},
            radius=[20],
            md_bg_color=self.theme_cls.accent_color,  # голубой
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )

        # === FloatLayout для центрирования иконок ===
        top_bar_container = MDFloatLayout(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # ✅ Центрирование
        )

        # === Контейнер для иконок — как у ребёнка (с фиксированным расстоянием) ===
        top_bar = MDBoxLayout(
            adaptive_size=True,
            size_hint_x=None,
            spacing=dp(20),  # ✅ Фиксированное расстояние
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # ✅ Центрирование всей группы
        )

        # Иконки
        icons = ["map.png", "book-open-variant.png", "account-child.png", "cog.png"]
        callbacks = [
            lambda: self.open_map_screen(),  # Замени lambda: print("Карта")
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

        # === Карусель фото — как у ребёнка ===
        carousel = MDCarousel(
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.18}  # ✅ Твоя позиция
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

        # === Список занятий в сером скруглённом прямоугольнике — приподнят ===
        self.lessons_card = MDCard(
            id='lessons_card',
            size_hint=(0.9, 0.5),  # ✅ Уменьшена высота
            pos_hint={'center_x': 0.5, 'center_y': 0.57},  # ✅ Твоя позиция
            radius=[15],
            md_bg_color=(0.9, 0.9, 0.9, 1),  # серый
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )

        lessons_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        lessons_layout.bind(minimum_height=lessons_layout.setter('height'))

        # Сортируем занятия по первому дню недели в списке (условно)
        sorted_lessons = sorted(self.lessons, key=lambda x: x.get("days_of_week", [])[0] if x.get("days_of_week") else "")
        if sorted_lessons:
            # nearest_day = sorted_lessons[0].get("days_of_week", [])[0] # Упрощаем
            for lesson in sorted_lessons:
                # is_nearest = (lesson.get("days_of_week", [])[0] == nearest_day) # Упрощаем
                is_nearest = False # Или реализовать логику ближайшего дня
                item = LessonItem(lesson, is_nearest=is_nearest)
                lessons_layout.add_widget(item)
        else:
            lessons_layout.add_widget(MDLabel(text="Нет занятий", halign="center"))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(lessons_layout)
        self.lessons_card.add_widget(scroll)
        layout.add_widget(self.lessons_card)

        # === Меню занятий (скрыто по умолчанию) ===
        self.lessons_menu = self.build_lessons_menu()
        self.lessons_menu.opacity = 0
        self.lessons_menu.disabled = True
        layout.add_widget(self.lessons_menu)

        # ✅ Обновляем цвета после построения интерфейса
        if self.app_ref:
            self.update_colors()

        self.add_widget(layout)

    def open_lessons_menu(self):
        # Плавно показываем меню занятий
        self.lessons_menu.disabled = False
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self.lessons_menu)

    def close_lessons_menu(self):
        # Плавно скрываем меню занятий
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *args: setattr(self.lessons_menu, 'disabled', True))
        anim.start(self.lessons_menu)

    def build_lessons_menu(self):
        menu = MDCard(
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            radius=[15],
            md_bg_color=(0.95, 0.95, 0.95, 1),  # светло-серый
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )

        # === Основной макет ===
        main_layout = MDBoxLayout(orientation="horizontal", spacing=dp(15))
        menu.add_widget(main_layout)

        # === Левая панель: список занятий ===
        left_panel = MDBoxLayout(orientation="vertical", size_hint_x=0.4, spacing=dp(10))

        # Заголовок
        left_panel.add_widget(MDLabel(text="Занятия", halign="center", bold=True, font_style="H6"))

        # Список занятий (с прокруткой)
        self.lessons_list_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.lessons_list_layout.bind(minimum_height=self.lessons_list_layout.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.lessons_list_layout)
        left_panel.add_widget(scroll)

        # Кнопка "Создать +" (внизу)
        btn_create = MDRaisedButton(
            text="+",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0, 0.5, 1, 1),  # синий
            on_release=lambda x: self.create_new_lesson()
        )
        left_panel.add_widget(btn_create)

        # Кнопка "Закрыть"
        btn_close = MDRaisedButton(
            text="Закрыть",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0.5, 0.5, 0.5, 1),  # серый
            on_release=lambda x: self.close_lessons_menu()
        )
        left_panel.add_widget(btn_close)

        main_layout.add_widget(left_panel)

        # === Правая панель: редактирование ===
        right_panel = MDBoxLayout(orientation="vertical", size_hint_x=0.6, spacing=dp(10))

        # Заголовок
        right_panel.add_widget(MDLabel(text="Редактирование", halign="center", bold=True, font_style="H6"))

        # Поле ввода названия
        self.title_field = MDTextField(hint_text="Название", size_hint_y=None, height=dp(50))
        right_panel.add_widget(self.title_field)

        # Поле для отображения выбранных дней недели
        self.days_display_field = MDTextField(
            hint_text="Дни недели",
            helper_text="Нажмите для выбора",
            mode="fill",
            size_hint_y=None,
            height=dp(50),
            readonly=True # Поле только для чтения
        )
        # Обработчик на нажатие
        original_on_touch_down = self.days_display_field.on_touch_down
        def custom_on_touch_down(touch):
            if self.days_display_field.collide_point(*touch.pos):
                self.open_days_selection_dialog() # Открываем диалог выбора дней
                return True
            return original_on_touch_down(touch) if original_on_touch_down else None
        self.days_display_field.on_touch_down = custom_on_touch_down

        right_panel.add_widget(self.days_display_field)

        # Кнопка "Удалить"
        btn_delete = MDRaisedButton(
            text="Удалить",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(1, 0, 0, 1),  # красный
            on_release=lambda x: self.delete_lesson()
        )
        right_panel.add_widget(btn_delete)

        # Кнопка "Сохранить"
        btn_save = MDRaisedButton(
            text="Сохранить",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0, 1, 0, 1),  # зелёный
            on_release=lambda x: self.save_lesson()
        )
        right_panel.add_widget(btn_save)

        main_layout.add_widget(right_panel)

        # === Заполняем список занятий ===
        self.update_lessons_list()

        return menu

    def open_days_selection_dialog(self):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.dialog import MDDialog
        # from kivy.uix.scrollview import ScrollView # Закомментируем, не используем

        # Список дней недели
        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

        # Получаем текущие выбранные дни из отображаемого поля
        current_days_text = self.days_display_field.text
        current_days = [day.strip() for day in current_days_text.split(", ") if day.strip()] if current_days_text else []

        # Словарь для хранения чекбоксов
        checkboxes = {}

        # Макет для чекбоксов - теперь он будет напрямую в content_cls
        checkboxes_layout = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        # Установим минимальную высоту, чтобы элементы отображались
        checkboxes_layout.bind(minimum_height=checkboxes_layout.setter('height'))

        for day in days_of_week:
            # Горизонтальный макет для чекбокса и лейбла
            row_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
            cb = MDCheckbox(size_hint=(None, None), size=(dp(48), dp(48)), active=(day in current_days))
            lbl = MDLabel(text=day, halign="left", valign="middle")
            # Убедимся, что лейбл правильно рассчитывает свой размер
            lbl.bind(texture_size=lbl.setter('size'))
            lbl.size_hint_x = 1 # Займет оставшееся место
            row_layout.add_widget(cb)
            row_layout.add_widget(lbl)
            checkboxes[day] = cb
            checkboxes_layout.add_widget(row_layout)

        # Кнопки диалога
        btn_ok = MDRaisedButton(
            text="ОК",
            on_release=lambda x: self.confirm_days_selection(checkboxes)
        )
        btn_cancel = MDRaisedButton(
            text="Отмена",
            on_release=lambda x: self.dialog.dismiss()
        )

        # Создаём диалог
        self.dialog = MDDialog(
            title="Выберите дни недели",
            type="custom",
            content_cls=checkboxes_layout, # Передаём макет напрямую
            buttons=[btn_ok, btn_cancel],
        )
        self.dialog.open()

    def confirm_days_selection(self, checkboxes_dict):
        selected_days = [day for day, checkbox in checkboxes_dict.items() if checkbox.active]
        # Обновляем отображаемое поле
        self.days_display_field.text = ", ".join(selected_days) if selected_days else ""
        # Закрываем диалог
        self.dialog.dismiss()

    def update_lessons_list(self):
        # Очищаем список
        self.lessons_list_layout.clear_widgets()

        # Добавляем кнопки для каждого занятия
        for lesson in self.lessons:
            # Создаём кнопку
            days_str = ", ".join(lesson.get("days_of_week", []))
            btn = MDRaisedButton(
                text=f"{lesson['title']} ({days_str})",
                size_hint_y=None,
                height=dp(50)
            )
            # Привязываем данные к кнопке
            btn.lesson_data = lesson
            # Назначаем обработчик
            btn.bind(on_release=lambda x: self.select_lesson(x.lesson_data))
            self.lessons_list_layout.add_widget(btn)

    def select_lesson(self, lesson):
        # Выбираем занятие для редактирования
        self.selected_lesson = lesson
        self.title_field.text = lesson["title"]
        # Предполагаем, что в данных теперь список дней недели
        days_list = lesson.get("days_of_week", [])
        self.days_display_field.text = ", ".join(days_list) if days_list else ""

    def create_new_lesson(self):
        # Создаём новое занятие
        new_lesson = {"title": "Без названия", "days_of_week": []} # Теперь список дней
        # Проверяем на дубликаты (по первому дню или по всем?)
        # Для простоты, проверим по названию, если список дней пуст
        if not new_lesson["days_of_week"]:
             new_lesson["title"] = get_unique_title(new_lesson["title"], new_lesson["days_of_week"], self.lessons)
        self.lessons.append(new_lesson)
        save_lessons(self.lessons)
        self.update_lessons_list()
        self.select_lesson(new_lesson)

    def delete_lesson(self):
        # Удаляем выбранное занятие
        if hasattr(self, 'selected_lesson'):
            self.lessons.remove(self.selected_lesson)
            save_lessons(self.lessons)
            self.update_lessons_list()
            self.title_field.text = ""
            self.days_display_field.text = "" # Сбрасываем поле дней недели

    def save_lesson(self):
        # Сохраняем изменения в занятии
        if hasattr(self, 'selected_lesson'):
            old_title = self.selected_lesson["title"]
            old_days = self.selected_lesson.get("days_of_week", [])

            new_title = self.title_field.text or "Без названия"
            # Получаем выбранные дни из отображаемого поля
            new_days_text = self.days_display_field.text
            new_days = [day.strip() for day in new_days_text.split(", ") if day.strip()] if new_days_text else []

            # Проверяем на дубликаты
            # Для простоты, будем проверять по названию и списку дней как строке
            # Можно улучшить логику проверки
            combined_old = f"{old_title}_{'_'.join(sorted(old_days))}"
            combined_new = f"{new_title}_{'_'.join(sorted(new_days))}"
            if combined_new != combined_old:
                 # Используем первый день из списка для проверки, если список не пуст
                 check_day = new_days[0] if new_days else ""
                 new_title = get_unique_title(new_title, check_day, self.lessons)

            self.selected_lesson["title"] = new_title
            self.selected_lesson["days_of_week"] = new_days # Сохраняем список дней

            save_lessons(self.lessons)
            self.update_lessons_list()
            self.select_lesson(self.selected_lesson)
            # Обновляем отображение списка занятий
            Clock.schedule_once(lambda dt: self.update_lessons_display())

    def update_lessons_display(self):
        # Обновляем отображение списка занятий на экране
        if hasattr(self, 'lessons_card'):
            # Пересоздаём содержимое
            self.lessons_card.clear_widgets()
            lessons_layout = MDGridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            lessons_layout.bind(minimum_height=lessons_layout.setter('height'))

            # Сортировка по первому дню недели в списке (условно)
            sorted_lessons = sorted(self.lessons, key=lambda x: x.get("days_of_week", [])[0] if x.get("days_of_week") else "")
            if sorted_lessons:
                # nearest_day = sorted_lessons[0].get("days_of_week", [])[0] # Упрощаем
                for lesson in sorted_lessons:
                    # is_nearest = (lesson.get("days_of_week", [])[0] == nearest_day) # Упрощаем
                    is_nearest = False # Или реализовать логику ближайшего дня
                    item = LessonItem(lesson, is_nearest=is_nearest)
                    lessons_layout.add_widget(item)
            else:
                lessons_layout.add_widget(MDLabel(text="Нет занятий", halign="center"))

            scroll = ScrollView(size_hint=(1, 1))
            scroll.add_widget(lessons_layout)
            self.lessons_card.add_widget(scroll)

    def open_settings(self):
        # Создаём новый экран настроек и добавляем его в ScreenManager
        settings_scr = SettingsScreen(parent_screen_instance=self)
        self.app_ref.root.add_widget(settings_scr)
        self.app_ref.root.current = "settings"

    def update_colors(self):
        # Обновляем цвета в зависимости от темы
        if self.app_ref.theme_cls.theme_style == "Dark":
            # Тёмная тема
            self.md_bg_color = (0.1, 0.1, 0.1, 1)  # тёмный фон
            if hasattr(self, 'lessons_card'):
                self.lessons_card.md_bg_color = (0.2, 0.2, 0.2, 1)  # тёмно-серый
            if hasattr(self, 'lessons_menu'):
                self.lessons_menu.md_bg_color = (0.25, 0.25, 0.25, 1) # чуть светлее
        else:
            # Светлая тема
            self.md_bg_color = (1, 1, 1, 1)  # белый фон
            if hasattr(self, 'lessons_card'):
                self.lessons_card.md_bg_color = (0.9, 0.9, 0.9, 1)  # светло-серый
            if hasattr(self, 'lessons_menu'):
                self.lessons_menu.md_bg_color = (0.95, 0.95, 0.95, 1) # чуть темнее

    def set_app_ref(self, app_ref):
        # Сохраняем ссылку на основное приложение
        self.app_ref = app_ref
        # Если интерфейс уже построен — обновляем цвета
        if hasattr(self, 'lessons_card'):
            self.update_colors()
        # Устанавливаем тип пользователя при передаче app_ref
        # Это может быть вызвано до установки current_user, но если current_user уже есть:
        if hasattr(app_ref, 'current_user') and app_ref.current_user:
            app_ref.current_user_type = "parent"  # Устанавливаем тип для родителя


class SettingsScreen(MDScreen):
    def __init__(self, parent_screen_instance, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.parent_screen = parent_screen_instance
        self.app_ref = parent_screen_instance.app_ref
        self.current_user = parent_screen_instance.current_user
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
        self.parent_screen.update_colors()

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

        user_data = users.get(self.current_user)
        if not user_data: # <--- Исправлено: user_data вместо user_
            print("Ошибка: пользователь не найден")
            return

        if user_data["password"] != hash_password(password):
            print("Неверный пароль")
            return

        # Удаляем сессию
        user_data.pop("session_token", None)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

        # Переходим на экран входа
        self.app_ref.root.current = "login"

    def go_back(self, instance):
        self.app_ref.root.current = "parent"