import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.graphics import Canvas
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from functools import partial
import hashlib
import string
import random
from datetime import datetime

# ─────────────────────────────────────────
# COLOR THEME (Professional Dark Theme)
# ─────────────────────────────────────────
COLORS = {
    'bg_primary': get_color_from_hex('#0A0E27'),
    'bg_secondary': get_color_from_hex('#141933'),
    'bg_card': get_color_from_hex('#1A2040'),
    'bg_card_hover': get_color_from_hex('#222B52'),
    'accent_primary': get_color_from_hex('#6C63FF'),
    'accent_secondary': get_color_from_hex('#5A52E0'),
    'accent_gradient': get_color_from_hex('#8B83FF'),
    'success': get_color_from_hex('#00D68F'),
    'danger': get_color_from_hex('#FF3D71'),
    'warning': get_color_from_hex('#FFAA00'),
    'text_primary': get_color_from_hex('#FFFFFF'),
    'text_secondary': get_color_from_hex('#8F9BB3'),
    'text_hint': get_color_from_hex('#5A6380'),
    'input_bg': get_color_from_hex('#1E2548'),
    'input_border': get_color_from_hex('#2E3663'),
    'divider': get_color_from_hex('#252D50'),
    'overlay': (0, 0, 0, 0.7),
    'transparent': (0, 0, 0, 0),
}


# ─────────────────────────────────────────
# CUSTOM WIDGETS
# ─────────────────────────────────────────
class RoundedBox(BoxLayout):
    """Rounded corner box with background color"""
    def __init__(self, bg_color=None, radius=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['bg_card']
        self.radius_val = radius or [dp(16)]
        self.bind(pos=self._update, size=self._update)
        Clock.schedule_once(lambda dt: self._update())

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self.radius_val
            )


class StyledTextInput(TextInput):
    """Professional styled text input"""
    def __init__(self, icon_text="", **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = COLORS['text_primary']
        self.cursor_color = COLORS['accent_primary']
        self.hint_text_color = COLORS['text_hint']
        self.font_size = sp(16)
        self.padding = [dp(20), dp(16), dp(20), dp(16)]
        self.multiline = False
        self.icon_text = icon_text
        self.bind(pos=self._draw_bg, size=self._draw_bg, focus=self._on_focus)
        Clock.schedule_once(lambda dt: self._draw_bg())

    def _draw_bg(self, *args):
        self.canvas.before.clear()
        border_color = COLORS['accent_primary'] if self.focus else COLORS['input_border']
        with self.canvas.before:
            Color(*COLORS['input_bg'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(*border_color)
            Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(14)
                ),
                width=dp(1.5) if self.focus else dp(1)
            )

    def _on_focus(self, *args):
        self._draw_bg()


class PrimaryButton(Button):
    """Gradient-style primary button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = COLORS['text_primary']
        self.font_size = sp(17)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(56)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        self.canvas.before.clear()
        color = COLORS['accent_secondary'] if self.state == 'down' else COLORS['accent_primary']
        with self.canvas.before:
            Color(*color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])


class SecondaryButton(Button):
    """Outlined secondary button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = COLORS['accent_primary']
        self.font_size = sp(15)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == 'down':
                Color(*COLORS['accent_primary'][:3], 0.15)
            else:
                Color(*COLORS['bg_card'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*COLORS['accent_primary'])
            Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(12)
                ),
                width=dp(1.5)
            )


class DangerButton(Button):
    """Red danger button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = COLORS['text_primary']
        self.font_size = sp(14)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(44)
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS['danger'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])


class PasswordCard(RoundedBox):
    """Professional password entry card"""
    def __init__(self, app_name, username, password, timestamp, on_delete, on_copy, **kwargs):
        super().__init__(
            bg_color=COLORS['bg_card'],
            radius=[dp(16)],
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=[dp(18), dp(14)],
            spacing=dp(6),
            **kwargs
        )
        self.app_name = app_name
        self.show_password = False
        self.password = password

        # Top row - App name and delete
        top_row = BoxLayout(size_hint_y=None, height=dp(32))

        # App icon circle
        icon_box = BoxLayout(size_hint_x=None, width=dp(32))
        icon_label = Label(
            text=app_name[0].upper() if app_name else "?",
            font_size=sp(16),
            bold=True,
            color=COLORS['text_primary']
        )
        icon_box.add_widget(icon_label)

        app_label = Label(
            text=f"  {app_name}",
            font_size=sp(18),
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            text_size=(dp(200), None)
        )

        delete_btn = Button(
            text="[color=#FF3D71]\u2716[/color]",
            markup=True,
            size_hint_x=None,
            width=dp(40),
            background_color=(0, 0, 0, 0),
            background_normal='',
            font_size=sp(18)
        )
        delete_btn.bind(on_press=lambda x: on_delete(app_name))

        top_row.add_widget(icon_box)
        top_row.add_widget(app_label)
        top_row.add_widget(delete_btn)

        # Username row
        user_row = BoxLayout(size_hint_y=None, height=dp(24))
        user_label = Label(
            text=f"  \U0001F464  {username}",
            font_size=sp(14),
            color=COLORS['text_secondary'],
            halign='left',
            text_size=(dp(300), None)
        )
        user_row.add_widget(user_label)

        # Password row
        pass_row = BoxLayout(size_hint_y=None, height=dp(28))
        self.pass_label = Label(
            text=f"  \U0001F512  {'•' * min(len(password), 12)}",
            font_size=sp(14),
            color=COLORS['text_secondary'],
            halign='left',
            text_size=(dp(200), None)
        )

        toggle_btn = Button(
            text="\U0001F441",
            size_hint_x=None,
            width=dp(40),
            background_color=(0, 0, 0, 0),
            background_normal='',
            font_size=sp(16)
        )
        toggle_btn.bind(on_press=self.toggle_password)

        copy_btn = Button(
            text="\U0001F4CB Copy",
            size_hint_x=None,
            width=dp(80),
            background_color=(0, 0, 0, 0),
            background_normal='',
            font_size=sp(13),
            color=COLORS['accent_primary']
        )
        copy_btn.bind(on_press=lambda x: on_copy(password))

        pass_row.add_widget(self.pass_label)
        pass_row.add_widget(toggle_btn)
        pass_row.add_widget(copy_btn)

        # Timestamp
        time_label = Label(
            text=f"  {timestamp}",
            font_size=sp(11),
            color=COLORS['text_hint'],
            halign='left',
            size_hint_y=None,
            height=dp(18),
            text_size=(dp(300), None)
        )

        self.add_widget(top_row)
        self.add_widget(user_row)
        self.add_widget(pass_row)
        self.add_widget(time_label)

    def toggle_password(self, *args):
        self.show_password = not self.show_password
        if self.show_password:
            self.pass_label.text = f"  \U0001F513  {self.password}"
        else:
            self.pass_label.text = f"  \U0001F512  {'•' * min(len(self.password), 12)}"


# ─────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────
class SplashScreen(Screen):
    """Professional Splash Screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        with layout.canvas.before:
            Color(*COLORS['bg_primary'])
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)

        # Logo area
        logo_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.6, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )

        shield_label = Label(
            text="\U0001F6E1",
            font_size=sp(72),
        )

        title = Label(
            text="Secure Vault",
            font_size=sp(32),
            bold=True,
            color=COLORS['text_primary']
        )

        subtitle = Label(
            text="Your passwords, protected.",
            font_size=sp(14),
            color=COLORS['text_secondary']
        )

        logo_box.add_widget(shield_label)
        logo_box.add_widget(title)
        logo_box.add_widget(subtitle)

        # Loading dots
        self.loading_label = Label(
            text="● ● ●",
            font_size=sp(24),
            color=COLORS['accent_primary'],
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.15}
        )

        # Version
        version_label = Label(
            text="v1.0 | Offline & Encrypted",
            font_size=sp(11),
            color=COLORS['text_hint'],
            size_hint=(1, 0.05),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        layout.add_widget(logo_box)
        layout.add_widget(self.loading_label)
        layout.add_widget(version_label)
        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.size = Window.size

    def on_enter(self):
        Clock.schedule_once(self.go_to_pin, 2.5)

    def go_to_pin(self, dt):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'pin'


class PinScreen(Screen):
    """Professional PIN Screen"""
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.entered_pin = ""
        self.is_setup = not store.exists("pin")

        layout = FloatLayout()
        with layout.canvas.before:
            Color(*COLORS['bg_primary'])
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)

        # Content
        content = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(10)
        )

        # Top spacing
        content.add_widget(Widget(size_hint_y=0.08))

        # Shield icon
        shield = Label(
            text="\U0001F512",
            font_size=sp(56),
            size_hint_y=0.12
        )

        # Title
        self.title_label = Label(
            text="Create PIN" if self.is_setup else "Enter PIN",
            font_size=sp(26),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=0.07
        )

        self.subtitle_label = Label(
            text="Set a 4-digit PIN to secure your vault" if self.is_setup
            else "Enter your PIN to unlock",
            font_size=sp(13),
            color=COLORS['text_secondary'],
            size_hint_y=0.05
        )

        # PIN dots
        self.dots_box = BoxLayout(
            size_hint=(0.5, 0.06),
            pos_hint={'center_x': 0.5},
            spacing=dp(20)
        )
        self.dots = []
        for i in range(4):
            dot = Label(
                text="○",
                font_size=sp(28),
                color=COLORS['text_hint']
            )
            self.dots.append(dot)
            self.dots_box.add_widget(dot)

        # Error label
        self.error_label = Label(
            text="",
            font_size=sp(13),
            color=COLORS['danger'],
            size_hint_y=0.04
        )

        content.add_widget(shield)
        content.add_widget(self.title_label)
        content.add_widget(self.subtitle_label)
        content.add_widget(Widget(size_hint_y=0.02))
        content.add_widget(self.dots_box)
        content.add_widget(self.error_label)
        content.add_widget(Widget(size_hint_y=0.02))

        # Numpad
        numpad = GridLayout(
            cols=3,
            size_hint=(0.85, 0.45),
            pos_hint={'center_x': 0.5},
            spacing=dp(12)
        )

        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '\u232B']
        for btn_text in buttons:
            if btn_text == '':
                numpad.add_widget(Widget())
            else:
                btn = Button(
                    text=btn_text,
                    font_size=sp(26) if btn_text != '\u232B' else sp(22),
                    background_color=(0, 0, 0, 0),
                    background_normal='',
                    color=COLORS['text_primary'],
                    bold=True
                )
                btn.bind(pos=self._draw_numpad_btn, size=self._draw_numpad_btn)
                Clock.schedule_once(partial(self._draw_numpad_btn_init, btn), 0.1)
                if btn_text == '\u232B':
                    btn.bind(on_press=self.backspace)
                else:
                    btn.bind(on_press=self.on_numpad_press)
                numpad.add_widget(btn)

        content.add_widget(numpad)
        layout.add_widget(content)
        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.size = Window.size

    def _draw_numpad_btn_init(self, btn, dt):
        self._draw_numpad_btn(btn)

    def _draw_numpad_btn(self, btn, *args):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*COLORS['bg_card'])
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(50)])

    def on_numpad_press(self, instance):
        if len(self.entered_pin) < 4:
            self.entered_pin += instance.text
            self.update_dots()

            if len(self.entered_pin) == 4:
                Clock.schedule_once(self.verify, 0.2)

    def backspace(self, instance):
        if self.entered_pin:
            self.entered_pin = self.entered_pin[:-1]
            self.update_dots()
            self.error_label.text = ""

    def update_dots(self):
        for i in range(4):
            if i < len(self.entered_pin):
                self.dots[i].text = "●"
                self.dots[i].color = COLORS['accent_primary']
            else:
                self.dots[i].text = "○"
                self.dots[i].color = COLORS['text_hint']

    def verify(self, dt):
        pin = self.entered_pin

        if self.is_setup:
            hashed = hashlib.sha256(pin.encode()).hexdigest()
            self.store.put("pin", value=hashed)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'main'
        else:
            stored_hash = self.store.get("pin")["value"]
            if hashlib.sha256(pin.encode()).hexdigest() == stored_hash:
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = 'main'
            else:
                self.error_label.text = "Wrong PIN. Try again."
                self.entered_pin = ""
                self.update_dots()
                self.shake_dots()

    def shake_dots(self):
        original_x = self.dots_box.x
        anim = (
            Animation(x=original_x - dp(10), duration=0.05) +
            Animation(x=original_x + dp(10), duration=0.05) +
            Animation(x=original_x - dp(8), duration=0.05) +
            Animation(x=original_x + dp(8), duration=0.05) +
            Animation(x=original_x, duration=0.05)
        )
        anim.start(self.dots_box)


class MainScreen(Screen):
    """Main Password Manager Screen"""
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store

        layout = FloatLayout()
        with layout.canvas.before:
            Color(*COLORS['bg_primary'])
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)

        content = BoxLayout(
            orientation='vertical',
            size_hint=(0.92, 0.96),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(12)
        )

        # ── Header ──
        header = BoxLayout(size_hint_y=None, height=dp(56))

        title_box = BoxLayout(orientation='vertical')
        header_title = Label(
            text="\U0001F6E1  Secure Vault",
            font_size=sp(22),
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            text_size=(dp(250), None)
        )
        header_sub = Label(
            text="    Your passwords are safe",
            font_size=sp(12),
            color=COLORS['text_secondary'],
            halign='left',
            text_size=(dp(250), None)
        )
        title_box.add_widget(header_title)
        title_box.add_widget(header_sub)

        # Settings button
        settings_btn = Button(
            text="\u2699",
            size_hint_x=None,
            width=dp(48),
            background_color=(0, 0, 0, 0),
            background_normal='',
            font_size=sp(24),
            color=COLORS['text_secondary']
        )
        settings_btn.bind(on_press=self.show_settings_popup)

        header.add_widget(title_box)
        header.add_widget(settings_btn)

        # ── Stats Bar ──
        self.stats_bar = RoundedBox(
            bg_color=COLORS['bg_card'],
            radius=[dp(14)],
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )

        self.total_label = Label(
            text="0\nTotal",
            font_size=sp(13),
            color=COLORS['text_primary'],
            halign='center',
            markup=True
        )
        self.recent_label = Label(
            text="0\nRecent",
            font_size=sp(13),
            color=COLORS['accent_primary'],
            halign='center',
            markup=True
        )

        self.stats_bar.add_widget(self.total_label)
        self.stats_bar.add_widget(self.recent_label)

        # ── Add Button ──
        add_btn = PrimaryButton(text="\u2795  Add New Password")
        add_btn.bind(on_press=self.show_add_popup)

        # ── Search ──
        self.search_input = StyledTextInput(hint_text="\U0001F50D  Search passwords...")
        self.search_input.size_hint_y = None
        self.search_input.height = dp(50)
        self.search_input.bind(text=self.on_search)

        # ── Password List ──
        self.list_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(12),
            padding=[0, dp(8)]
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            bar_color=COLORS['accent_primary']
        )
        scroll.add_widget(self.list_layout)

        # ── Empty State ──
        self.empty_label = Label(
            text="\U0001F4AD\n\nNo passwords saved yet\nTap + to add your first password",
            font_size=sp(15),
            color=COLORS['text_hint'],
            halign='center',
            valign='middle',
            markup=True
        )

        # Assemble
        content.add_widget(header)
        content.add_widget(self.stats_bar)
        content.add_widget(add_btn)
        content.add_widget(self.search_input)
        content.add_widget(scroll)

        layout.add_widget(content)
        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.size = Window.size

    def on_enter(self):
        self.load_passwords()

    def on_search(self, instance, value):
        self.load_passwords(search=value.strip().lower())

    def load_passwords(self, search=""):
        self.list_layout.clear_widgets()
        count = 0

        keys = [k for k in self.store.keys() if k != "pin"]

        if search:
            keys = [k for k in keys if search in k.lower()]

        for key in sorted(keys):
            data = self.store.get(key)
            timestamp = data.get('timestamp', 'Unknown date')

            card = PasswordCard(
                app_name=key,
                username=data.get('username', ''),
                password=data.get('password', ''),
                timestamp=timestamp,
                on_delete=self.confirm_delete,
                on_copy=self.copy_to_clipboard
            )
            self.list_layout.add_widget(card)
            count += 1

        # Update stats
        total = len([k for k in self.store.keys() if k != "pin"])
        self.total_label.text = f"[b]{total}[/b]\nTotal"
        self.total_label.markup = True
        self.recent_label.text = f"[b]{min(count, total)}[/b]\nShowing"
        self.recent_label.markup = True

        # Empty state
        if count == 0:
            self.list_layout.add_widget(
                Label(
                    text="\U0001F4AD\n\nNo passwords found",
                    font_size=sp(15),
                    color=COLORS['text_hint'],
                    halign='center',
                    size_hint_y=None,
                    height=dp(150)
                )
            )

    def show_add_popup(self, *args):
        popup_content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(14)
        )

        with popup_content.canvas.before:
            Color(*COLORS['bg_secondary'])
            self.popup_bg = RoundedRectangle(
                pos=popup_content.pos,
                size=popup_content.size,
                radius=[dp(20)]
            )
        popup_content.bind(
            pos=lambda *a: setattr(self.popup_bg, 'pos', popup_content.pos),
            size=lambda *a: setattr(self.popup_bg, 'size', popup_content.size)
        )

        # Title
        popup_title = Label(
            text="\U0001F4DD  Add New Password",
            font_size=sp(20),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(36)
        )

        # Input fields
        self.popup_app_input = StyledTextInput(hint_text="App / Website Name")
        self.popup_app_input.size_hint_y = None
        self.popup_app_input.height = dp(52)

        self.popup_user_input = StyledTextInput(hint_text="Username / Email")
        self.popup_user_input.size_hint_y = None
        self.popup_user_input.height = dp(52)

        self.popup_pass_input = StyledTextInput(hint_text="Password")
        self.popup_pass_input.password = True
        self.popup_pass_input.size_hint_y = None
        self.popup_pass_input.height = dp(52)

        # Generate password button
        gen_btn = SecondaryButton(text="\U0001F3B2  Generate Strong Password")
        gen_btn.bind(on_press=self.generate_password)

        # Error label
        self.popup_error = Label(
            text="",
            font_size=sp(12),
            color=COLORS['danger'],
            size_hint_y=None,
            height=dp(20)
        )

        # Buttons
        btn_row = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(52))

        cancel_btn = SecondaryButton(text="Cancel")
        save_btn = PrimaryButton(text="Save")

        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        save_btn.bind(on_press=self.save_from_popup)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)

        popup_content.add_widget(popup_title)
        popup_content.add_widget(Widget(size_hint_y=None, height=dp(4)))
        popup_content.add_widget(self.popup_app_input)
        popup_content.add_widget(self.popup_user_input)
        popup_content.add_widget(self.popup_pass_input)
        popup_content.add_widget(gen_btn)
        popup_content.add_widget(self.popup_error)
        popup_content.add_widget(Widget(size_hint_y=0.1))
        popup_content.add_widget(btn_row)

        self.popup = Popup(
            title="",
            separator_height=0,
            content=popup_content,
            size_hint=(0.92, 0.72),
            background_color=COLORS['overlay'],
            background='',
            auto_dismiss=True
        )
        self.popup.open()

    def generate_password(self, *args):
        chars = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(random.choice(chars) for _ in range(16))
        self.popup_pass_input.text = password
        self.popup_pass_input.password = False

    def save_from_popup(self, *args):
        app = self.popup_app_input.text.strip()
        user = self.popup_user_input.text.strip()
        pwd = self.popup_pass_input.text.strip()

        if not app:
            self.popup_error.text = "App name is required"
            return
        if not user:
            self.popup_error.text = "Username is required"
            return
        if not pwd:
            self.popup_error.text = "Password is required"
            return
        if len(pwd) < 4:
            self.popup_error.text = "Password too short (min 4 chars)"
            return

        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.store.put(app, username=user, password=pwd, timestamp=timestamp)

        self.popup.dismiss()
        self.load_passwords()
        self.show_toast("Password saved successfully!")

    def confirm_delete(self, key):
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(16)
        )

        with content.canvas.before:
            Color(*COLORS['bg_secondary'])
            self.del_bg = RoundedRectangle(
                pos=content.pos,
                size=content.size,
                radius=[dp(20)]
            )
        content.bind(
            pos=lambda *a: setattr(self.del_bg, 'pos', content.pos),
            size=lambda *a: setattr(self.del_bg, 'size', content.size)
        )

        warn_icon = Label(
            text="\u26A0",
            font_size=sp(48),
            size_hint_y=0.3
        )

        msg = Label(
            text=f"Delete '{key}'?\n\nThis action cannot be undone.",
            font_size=sp(15),
            color=COLORS['text_secondary'],
            halign='center',
            size_hint_y=0.3
        )

        btn_row = BoxLayout(spacing=dp(12), size_hint_y=0.25)

        cancel_btn = SecondaryButton(text="Cancel")
        delete_btn = DangerButton(text="Delete")

        def do_delete(x):
            self.store.delete(key)
            self.load_passwords()
            del_popup.dismiss()
            self.show_toast(f"'{key}' deleted")

        cancel_btn.bind(on_press=lambda x: del_popup.dismiss())
        delete_btn.bind(on_press=do_delete)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(delete_btn)

        content.add_widget(warn_icon)
        content.add_widget(msg)
        content.add_widget(btn_row)

        del_popup = Popup(
            title="",
            separator_height=0,
            content=content,
            size_hint=(0.8, 0.4),
            background_color=COLORS['overlay'],
            background='',
        )
        del_popup.open()

    def copy_to_clipboard(self, text):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self.show_toast("Password copied!")
        except Exception:
            self.show_toast("Copy not supported")

    def show_toast(self, message):
        toast_label = Label(
            text=message,
            font_size=sp(14),
            color=COLORS['text_primary'],
            size_hint=(0.7, None),
            height=dp(44),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        toast_box = FloatLayout(size_hint=(1, 1))
        bg_box = BoxLayout(
            size_hint=(0.7, None),
            height=dp(44),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        with bg_box.canvas.before:
            Color(*COLORS['success'][:3], 0.9)
            self.toast_rect = RoundedRectangle(
                pos=bg_box.pos,
                size=bg_box.size,
                radius=[dp(22)]
            )
        bg_box.bind(
            pos=lambda *a: setattr(self.toast_rect, 'pos', bg_box.pos),
            size=lambda *a: setattr(self.toast_rect, 'size', bg_box.size)
        )

        toast_box.add_widget(bg_box)
        toast_box.add_widget(toast_label)

        self.add_widget(toast_box)

        def remove_toast(dt):
            self.remove_widget(toast_box)

        Clock.schedule_once(remove_toast, 2)

    def show_settings_popup(self, *args):
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(14)
        )

        with content.canvas.before:
            Color(*COLORS['bg_secondary'])
            self.settings_bg = RoundedRectangle(
                pos=content.pos,
                size=content.size,
                radius=[dp(20)]
            )
        content.bind(
            pos=lambda *a: setattr(self.settings_bg, 'pos', content.pos),
            size=lambda *a: setattr(self.settings_bg, 'size', content.size)
        )

        title = Label(
            text="\u2699  Settings",
            font_size=sp(22),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(36)
        )

        # Change PIN
        change_pin_btn = SecondaryButton(text="\U0001F512  Change PIN")
        change_pin_btn.bind(on_press=lambda x: self.change_pin(settings_popup))

        # Export
        export_btn = SecondaryButton(text="\U0001F4E4  Export Passwords")
        export_btn.bind(on_press=lambda x: self.export_passwords(settings_popup))

        # About
        about_label = Label(
            text="Secure Vault v1.0\nOffline Password Manager\nAll data stored locally",
            font_size=sp(12),
            color=COLORS['text_hint'],
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )

        # Close
        close_btn = PrimaryButton(text="Close")
        close_btn.bind(on_press=lambda x: settings_popup.dismiss())

        # Lock
        lock_btn = DangerButton(text="\U0001F512  Lock Vault")
        lock_btn.bind(on_press=lambda x: self.lock_vault(settings_popup))

        content.add_widget(title)
        content.add_widget(Widget(size_hint_y=None, height=dp(8)))
        content.add_widget(change_pin_btn)
        content.add_widget(export_btn)
        content.add_widget(lock_btn)
        content.add_widget(Widget(size_hint_y=0.1))
        content.add_widget(about_label)
        content.add_widget(close_btn)

        settings_popup = Popup(
            title="",
            separator_height=0,
            content=content,
            size_hint=(0.88, 0.65),
            background_color=COLORS['overlay'],
            background='',
        )
        settings_popup.open()

    def change_pin(self, popup):
        popup.dismiss()

        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(14)
        )

        with content.canvas.before:
            Color(*COLORS['bg_secondary'])
            self.cp_bg = RoundedRectangle(
                pos=content.pos, size=content.size, radius=[dp(20)]
            )
        content.bind(
            pos=lambda *a: setattr(self.cp_bg, 'pos', content.pos),
            size=lambda *a: setattr(self.cp_bg, 'size', content.size)
        )

        title = Label(
            text="Change PIN",
            font_size=sp(20),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(36)
        )

        old_pin = StyledTextInput(hint_text="Current PIN")
        old_pin.password = True
        old_pin.size_hint_y = None
        old_pin.height = dp(52)

        new_pin = StyledTextInput(hint_text="New PIN (4 digits)")
        new_pin.password = True
        new_pin.size_hint_y = None
        new_pin.height = dp(52)

        error_label = Label(
            text="", font_size=sp(12),
            color=COLORS['danger'],
            size_hint_y=None, height=dp(20)
        )

        btn_row = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(52))
        cancel_btn = SecondaryButton(text="Cancel")
        save_btn = PrimaryButton(text="Change")

        def do_change(x):
            old = old_pin.text.strip()
            new = new_pin.text.strip()
            stored = self.store.get("pin")["value"]

            if hashlib.sha256(old.encode()).hexdigest() != stored:
                error_label.text = "Current PIN is wrong"
                return
            if len(new) != 4 or not new.isdigit():
                error_label.text = "New PIN must be 4 digits"
                return

            self.store.put("pin", value=hashlib.sha256(new.encode()).hexdigest())
            pin_popup.dismiss()
            self.show_toast("PIN changed!")

        cancel_btn.bind(on_press=lambda x: pin_popup.dismiss())
        save_btn.bind(on_press=do_change)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)

        content.add_widget(title)
        content.add_widget(old_pin)
        content.add_widget(new_pin)
        content.add_widget(error_label)
        content.add_widget(Widget(size_hint_y=0.1))
        content.add_widget(btn_row)

        pin_popup = Popup(
            title="", separator_height=0,
            content=content,
            size_hint=(0.88, 0.55),
            background_color=COLORS['overlay'],
            background=''
        )
        pin_popup.open()

    def export_passwords(self, popup):
        popup.dismiss()
        try:
            data = {}
            for key in self.store.keys():
                if key != "pin":
                    data[key] = dict(self.store.get(key))

            export_path = os.path.join(
                os.path.expanduser("~"),
                "vault_export.json"
            )
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)

            self.show_toast(f"Exported to {export_path}")
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}")

    def lock_vault(self, popup):
        popup.dismiss()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'pin'


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────
class SecureVault(App):
    def build(self):
        self.title = "Secure Vault"
        Window.clearcolor = COLORS['bg_primary']

        self.store = JsonStore("vault.json")

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(PinScreen(store=self.store, name='pin'))
        sm.add_widget(MainScreen(store=self.store, name='main'))

        return sm


if __name__ == "__main__":
    SecureVault().run()
