import sys
import os
garden_mapview_path = os.path.join(os.path.expanduser("~"), ".kivy", "garden", "garden.mapview")
internal_mapview_path = os.path.join(garden_mapview_path, "mapview")
if internal_mapview_path not in sys.path:
    sys.path.insert(0, internal_mapview_path)
if garden_mapview_path not in sys.path:
    sys.path.insert(0, garden_mapview_path)
import importlib.util
mapview_init_path = os.path.join(garden_mapview_path, "__init__.py")
if os.path.exists(mapview_init_path):
    spec = importlib.util.spec_from_file_location("garden.mapview", mapview_init_path)
    mapview_module = importlib.util.module_from_spec(spec)
    sys.modules["garden.mapview"] = mapview_module
    spec.loader.exec_module(mapview_module)
    MapView = getattr(mapview_module, 'MapView')
    MapMarker = getattr(mapview_module, 'MapMarker')
else:
    raise ImportError(f"Файл __init__.py для garden.mapview не найден по пути: {mapview_init_path}")
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
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
        title_label = MDLabel(
            text="Карта",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(50),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )
        layout.add_widget(title_label)
        back_btn = MDRaisedButton(
            text="Назад",
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'x': 0.02, 'top': 0.98},
            on_release=self.go_back
        )
        layout.add_widget(back_btn)
        self.map_widget = MapView(
            zoom=13,
            lat=62.53,
            lon=114.03,
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        layout.add_widget(self.map_widget)
        marker = MapMarker(lat=62.53, lon=114.03)
        self.map_widget.add_marker(marker)
        location_btn = MDRaisedButton(
            text="Моё местоположение",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            on_release=self.request_location_update
        )
        layout.add_widget(location_btn)
        layout.add_widget(Image(
            source='foto.png',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            pos_hint={'right': 1, 'y': 0},
            allow_stretch=True,
            keep_ratio=True
        ))
        self.add_widget(layout)
    def go_back(self, instance):
        self.stop_location_updates()
        self.app_ref.root.current = "main" if self.app_ref.current_user_type == "main" else "parent"
    def request_location_update(self, instance):
        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start()
        except NotImplementedError:
            print("GPS не поддерживается на этой платформе.")
    def on_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            self.gps_location = (lat, lon)
            print(f"GPS: {lat}, {lon}")
            if self.current_marker:
                self.map_widget.remove_marker(self.current_marker)
            self.current_marker = MapMarker(lat=lat, lon=lon)
            self.map_widget.add_marker(self.current_marker)
            self.map_widget.center_on(lat, lon)
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
            pass
from kivy.uix.image import Image