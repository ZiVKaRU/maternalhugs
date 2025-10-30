# map_screen.py
import sys
import os
import importlib.util

# Путь к установленному garden-пакету mapview
garden_mapview_path = os.path.join(os.path.expanduser("~"), ".kivy", "garden", "garden.mapview")
# Путь к подпапке mapview внутри garden.mapview
internal_mapview_path = os.path.join(garden_mapview_path, "mapview")

# Добавляем внутреннюю папку в sys.path, чтобы она могла импортировать свои модули
if internal_mapview_path not in sys.path:
    sys.path.insert(0, internal_mapview_path)

# Также добавляем корневую папку garden.mapview
if garden_mapview_path not in sys.path:
    sys.path.insert(0, garden_mapview_path)

# Теперь динамически загружаем модуль garden.mapview
mapview_init_path = os.path.join(garden_mapview_path, "__init__.py")

if os.path.exists(mapview_init_path):
    spec = importlib.util.spec_from_file_location("garden.mapview", mapview_init_path)
    mapview_module = importlib.util.module_from_spec(spec)
    sys.modules["garden.mapview"] = mapview_module
    spec.loader.exec_module(mapview_module)

    # Теперь можно получить классы из модуля
    MapView = getattr(mapview_module, 'MapView')
    MapMarker = getattr(mapview_module, 'MapMarker')
else:
    raise ImportError(f"Файл __init__.py для garden.mapview не найден по пути: {mapview_init_path}")


from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
# from kivy_garden.mapview import MapView, MapMarker # Теперь не нужно
from plyer import gps
from kivy.clock import Clock
from kivy.app import App
import json


def get_locations_path():
    return os.path.join(App.get_running_app().user_data_dir, "locations.json")


def load_locations():
    path = get_locations_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_locations(locations):
    path = get_locations_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(locations, f, indent=4, ensure_ascii=False)


class MapScreen(MDScreen):
    def __init__(self, parent_app_instance, **kwargs):
        super().__init__(**kwargs)
        self.name = "map"
        self.parent_app = parent_app_instance
        self.app_ref = parent_app_instance
        self.map_widget = None
        self.current_marker = None
        self.gps_location = None
        self.build_ui()

    def build_ui(self):
        layout = MDFloatLayout()

        # Надпись "Карта" сверху
        title_label = MDLabel(
            text="Карта",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(50),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )
        layout.add_widget(title_label)

        # Кнопка "Назад"
        back_btn = MDRaisedButton(
            text="Назад",
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'x': 0.02, 'top': 0.98},
            on_release=self.go_back
        )
        layout.add_widget(back_btn)

        # Карта (прямоугольник сверху)
        self.map_widget = MapView(
            zoom=13,  # Приблизим немного
            lat=62.53,  # Примерная широта Мирного (Якутия)
            lon=114.03, # Примерная долгота Мирного (Якутия)
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'top': 0.9} # Отступ от верха под заголовок и кнопку
        )
        layout.add_widget(self.map_widget)

        # Попробуем добавить маркер для Мирного
        marker = MapMarker(lat=62.53, lon=114.03)
        # marker.source = 'marker.png' # Если хочешь свою иконку, положи файл в папку с проектом
        self.map_widget.add_marker(marker)

        # Кнопка для обновления местоположения (если доступно)
        location_btn = MDRaisedButton(
            text="Моё местоположение",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            on_release=self.request_location_update
        )
        layout.add_widget(location_btn)

        self.add_widget(layout)

    def go_back(self, instance):
        # Остановить GPS при выходе
        self.stop_location_updates()
        self.app_ref.root.current = "main" if self.app_ref.current_user_type == "main" else "parent"

    def request_location_update(self, instance):
        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start()
        except NotImplementedError:
            print("GPS не поддерживается на этой платформе.")

    def on_location(self, **kwargs):
        # kwargs содержит 'lat', 'lon', 'speed', 'bearing', 'altitude', 'accuracy'
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            self.gps_location = (lat, lon)
            print(f"GPS: {lat}, {lon}")
            # Удаляем старый маркер, если был
            if self.current_marker:
                self.map_widget.remove_marker(self.current_marker)
            # Добавляем маркер для текущего местоположения
            self.current_marker = MapMarker(lat=lat, lon=lon)
            # self.current_marker.source = 'current_marker.png' # Или стандартный маркер
            self.map_widget.add_marker(self.current_marker)
            # Центрируем карту на текущем местоположении
            self.map_widget.center_on(lat, lon)
            # Сохраняем последнее известное местоположение
            if self.parent_app.current_user:
                locations = load_locations()
                user_locations = locations.get(self.parent_app.current_user, [])
                user_locations.append({"lat": lat, "lon": lon, "timestamp": Clock.get_time()})
                locations[self.parent_app.current_user] = user_locations
                save_locations(locations)

    def on_status(self, stype, status):
        print(f"GPS Status: {stype}, {status}")

    def stop_location_updates(self):
        try:
            gps.stop()
        except NotImplementedError:
            pass # Или вывести сообщение, если не поддерживается