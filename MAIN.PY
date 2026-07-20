import os
import hashlib
import string
import random
from datetime import datetime

from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex


# =========================
# THEME
# =========================
COLORS = {
    "bg": get_color_from_hex("#0B1020"),
    "card": get_color_from_hex("#151C33"),
    "card2": get_color_from_hex("#1B2442"),
    "input": get_color_from_hex("#121A30"),
    "border": get_color_from_hex("#2B355A"),
    "accent": get_color_from_hex("#6C63FF"),
    "accent_dark": get_color_from_hex("#5B53E6"),
    "success": get_color_from_hex("#00C48C"),
    "danger": get_color_from_hex("#FF4D67"),
    "text": get_color_from_hex("#FFFFFF"),
    "subtext": get_color_from_hex("#A8B1CF"),
    "hint": get_color_from_hex("#6E7899"),
}


# =========================
# CUSTOM WIDGETS
# =========================
class RoundedBox(BoxLayout):
    def __init__(self, bg_color=None, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS["card"]
        self.radius = radius
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self.radius)])


class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = COLORS["text"]
        self.cursor_color = COLORS["accent"]
        self.hint_text_color = COLORS["hint"]
        self.multiline = False
        self.font_size = sp(16)
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.bind(pos=self._redraw, size=self._redraw, focus=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *args):
        border = COLORS["accent"] if self.focus else COLORS["border"]
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["input"])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*border)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.4)
            )


class PrimaryButton(Button):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.btn_color = bg_color or COLORS["accent"]
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = COLORS["text"]
        self.bold = True
        self.font_size = sp(16)
        self.size_hint_y = None
        self.height = dp(52)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *args):
        color = COLORS["accent_dark"] if self.state == "down" else self.btn_color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class SecondaryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = COLORS["accent"]
        self.bold = True
        self.font_size = sp(15)
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["card2"])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*COLORS["accent"])
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.3)
            )


class NumpadButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = COLORS["text"]
        self.bold = True
        self.font_size = sp(24)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *args):
        bg = COLORS["card2"] if self.state == "down" else COLORS["card"]
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(40)])


# =========================
# SPLASH SCREEN
# =========================
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = FloatLayout()

        with root.canvas.before:
            Color(*COLORS["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)

        root.bind(size=self._update_bg, pos=self._update_bg)

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint=(0.8, 0.35),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
        )

        box.add_widget(Label(text="SECURE VAULT", font_size=sp(32), bold=True, color=COLORS["text"]))
        box.add_widget(Label(text="Offline Password Protection", font_size=sp(14), color=COLORS["subtext"]))
        box.add_widget(Label(text="Loading...", font_size=sp(12), color=COLORS["hint"]))

        root.add_widget(box)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.size = Window.size

    def on_enter(self):
        Clock.schedule_once(self.go_next, 1.8)

    def go_next(self, dt):
        if self.manager:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "pin"


# =========================
# PIN SCREEN
# =========================
class PinScreen(Screen):
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.entered_pin = ""

        root = FloatLayout()
        with root.canvas.before:
            Color(*COLORS["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)
        root.bind(size=self._update_bg, pos=self._update_bg)

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(0.86, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        content.add_widget(Widget(size_hint_y=0.08))

        self.title_label = Label(
            text="Create PIN",
            font_size=sp(26),
            bold=True,
            color=COLORS["text"],
            size_hint_y=0.08,
        )

        self.sub_label = Label(
            text="Set a 
