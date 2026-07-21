Import os
import hashlib
import string
import random
from datetime import datetime

from kivy.app import App
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
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex


# ─────────────────────────────────────
# THEME
# ─────────────────────────────────────
C = {
    "bg": get_color_from_hex("#0A0E27"),
    "card": get_color_from_hex("#161C36"),
    "card2": get_color_from_hex("#1D2445"),
    "accent": get_color_from_hex("#6C63FF"),
    "accent_dark": get_color_from_hex("#554DDB"),
    "text": get_color_from_hex("#FFFFFF"),
    "subtext": get_color_from_hex("#9DA7C2"),
    "hint": get_color_from_hex("#64708E"),
    "green": get_color_from_hex("#00C48C"),
    "red": get_color_from_hex("#FF4D67"),
    "border": get_color_from_hex("#2A335D"),
    "input_bg": get_color_from_hex("#11182F"),
}


# ─────────────────────────────────────
# HELPERS
# ─────────────────────────────────────
def sha_pin(pin_text):
    return hashlib.sha256(pin_text.encode("utf-8")).hexdigest()


# ─────────────────────────────────────
# CUSTOM WIDGETS
# ─────────────────────────────────────
class RoundedBox(BoxLayout):
    def __init__(self, bg_color=None, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or C["card"]
        self.radius_value = radius
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        Clock.schedule_once(lambda dt: self._update_canvas())

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius_value)]
            )


class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = C["text"]
        self.cursor_color = C["accent"]
        self.hint_text_color = C["hint"]
        self.font_size = sp(15)
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.bind(pos=self._draw, size=self._draw, focus=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        border = C["accent"] if self.focus else C["border"]
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C["input_bg"])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(*border)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.2)
            )


class FilledButton(Button):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.btn_bg = bg_color or C["accent"]
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = C["text"]
        self.font_size = sp(15)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(52)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        bg = C["accent_dark"] if self.state == "down" else self.btn_bg
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*bg)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )


class OutlineButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = C["accent"]
        self.font_size = sp(14)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C["card2"])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(*C["accent"])
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.1)
            )


# ─────────────────────────────────────
# SPLASH SCREEN
# ─────────────────────────────────────
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = FloatLayout()
        with root.canvas.before:
            Color(*C["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)

        root.bind(pos=self._update_bg, size=self._update_bg)

        center_box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint=(0.8, 0.35),
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )

        center_box.add_widget(Label(
            text="Secure Vault",
            font_size=sp(30),
            bold=True,
            color=C["text"]
        ))
        center_box.add_widget(Label(
            text="Offline Password Manager",
            font_size=sp(14),
            color=C["subtext"]
        ))
        center_box.add_widget(Label(
            text="Fast • Private • Secure",
            font_size=sp(12),
            color=C["hint"]
        ))

        version_label = Label(
            text="v1.0",
            font_size=sp(11),
            color=C["hint"],
            size_hint=(1, 0.05),
            pos_hint={"center_x": 0.5, "y": 0.03}
        )

        root.add_widget(center_box)
        root.add_widget(version_label)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = Window.size

    def on_enter(self):
        Clock.schedule_once(self.go_next, 1.8)

    def go_next(self, dt):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "pin"


# ─────────────────────────────────────
# PIN SCREEN
# ─────────────────────────────────────
class PinScreen(Screen):
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.pin_text = ""

        root = FloatLayout()
        with root.canvas.before:
            Color(*C["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)

        root.bind(pos=self._update_bg, size=self._update_bg)

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(0.86, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        content.add_widget(Widget(size_hint_y=0.08))

        self.title_label = Label(
            text="Enter PIN",
            font_size=sp(25),
            bold=True,
            color=C["text"],
            size_hint_y=0.08
        )
        self.subtitle_label = Label(
            text="Unlock your vault",
            font_size=sp(13),
            color=C["subtext"],
            size_hint_y=0.04
        )

        self.dots_box = BoxLayout(
            size_hint=(0.42, 0.06),
            pos_hint={"center_x": 0.5},
            spacing=dp(14)
        )
        self.dots = []
        for _ in range(4):
            dot = Label(
                text="○",
                font_size=sp(28),
                color=C["hint"]
            )
            self.dots.append(dot)
            self.dots_box.add_widget(dot)

        self.error_label = Label(
            text="",
            font_size=sp(13),
            color=C["red"],
            size_hint_y=0.04
        )

        content.add_widget(self.title_label)
        content.add_widget(self.subtitle_label)
        content.add_widget(Widget(size_hint_y=0.02))
        content.add_widget(self.dots_box)
        content.add_widget(self.error_label)
        content.add_widget(Widget(size_hint_y=0.03))

        keypad = GridLayout(
            cols=3,
            spacing=dp(12),
            size_hint=(0.82, 0.48),
            pos_hint={"center_x": 0.5}
        )

        for txt in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"]:
            if txt == "":
                keypad.add_widget(Widget())
            else:
                btn = Button(
                    text=txt,
                    background_color=(0, 0, 0, 0),
                    background_normal="",
                    color=C["text"],
                    font_size=sp(24),
                    bold=True
                )
                btn.bind(pos=self._draw_key, size=self._draw_key, state=self._draw_key)
                if txt == "⌫":
                    btn.bind(on_press=self.on_backspace)
                else:
                    btn.bind(on_press=self.on_key_press)
                keypad.add_widget(btn)

        content.add_widget(keypad)
        root.add_widget(content)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = Window.size

    def _draw_key(self, btn, *args):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*C["card"])
            RoundedRectangle(
                pos=btn.pos,
                size=btn.size,
                radius=[dp(40)]
            )

    def on_pre_enter(self, *args):
        self.pin_text = ""
        self.error_label.text = ""
        self.update_dots()

        is_new = not self.store.exists("pin")
        if is_new:
            self.title_label.text = "Create PIN"
            self.subtitle_label.text = "Set a 4-digit PIN for your vault"
        else:
            self.title_label.text = "Enter PIN"
            self.subtitle_label.text = "Unlock your vault"

    def on_key_press(self, instance):
        if len(self.pin_text) < 4:
            self.pin_text += instance.text
            self.update_dots()
            if len(self.pin_text) == 4:
                Clock.schedule_once(self.verify_pin, 0.15)

    def on_backspace(self, *args):
        if self.pin_text:
            self.pin_text = self.pin_text[:-1]
            self.error_label.text = ""
            self.update_dots()

    def update_dots(self):
        for i in range(4):
            if i < len(self.pin_text):
                self.dots[i].text = "●"
                self.dots[i].color = C["accent"]
            else:
                self.dots[i].text = "○"
                self.dots[i].color = C["hint"]

    def verify_pin(self, dt):
        current_pin = self.pin_text
        is_new = not self.store.exists("pin")

        if is_new:
            self.store.put("pin", value=sha_pin(current_pin))
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "main"
            return

        saved_hash = self.store.get("pin")["value"]
        if sha_pin(current_pin) == saved_hash:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "main"
        else:
            self.error_label.text = "Wrong PIN. Try again."
            self.pin_text = ""
            self.update_dots()
            self.shake()

    def shake(self):
        original_x = self.dots_box.x
        anim = (
            Animation(x=original_x - dp(10), duration=0.05) +
            Animation(x=original_x + dp(10), duration=0.05) +
            Animation(x=original_x - dp(6), duration=0.05) +
            Animation(x=original_x + dp(6), duration=0.05) +
            Animation(x=original_x, duration=0.05)
        )
        anim.start(self.dots_box)


# ─────────────────────────────────────
# MAIN SCREEN
# ─────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.add_popup = None

        root = FloatLayout()
        with root.canvas.before:
            Color(*C["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)

        root.bind(pos=self._update_bg, size=self._update_bg)

        wrapper = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint=(0.92, 0.96),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(54))

        header_left = BoxLayout(orientation="vertical")
        header_left.add_widget(Label(
            text="Secure Vault",
            font_size=sp(22),
            bold=True,
            color=C["text"],
            halign="left",
            text_size=(dp(240), None)
        ))
        header_left.add_widget(Label(
            text="Your passwords are stored locally",
            font_size=sp(12),
            color=C["subtext"],
            halign="left",
            text_size=(dp(260), None)
        ))

        lock_btn = Button(
            text="LOCK",
            size_hint_x=None,
            width=dp(70),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=C["accent"],
            bold=True
        )
        lock_btn.bind(pos=self._draw_lock_btn, size=self._draw_lock_btn, state=self._draw_lock_btn)
        lock_btn.bind(on_press=self.lock_vault)

        header.add_widget(header_left)
        header.add_widget(lock_btn)

        # Stats
        self.stats_box = RoundedBox(
            bg_color=C["card"],
            radius=14,
            size_hint_y=None,
            height=dp(62),
            padding=[dp(16), dp(10)],
            spacing=dp(10)
        )

        self.total_label = Label(
            text="0\nTotal",
            font_size=sp(13),
            color=C["text"],
            halign="center",
            markup=True
        )
        self.showing_label = Label(
            text="0\nShowing",
            font_size=sp(13),
            color=C["accent"],
            halign="center",
            markup=True
        )

        self.stats_box.add_widget(self.total_label)
        self.stats_box.add_widget(self.showing_label)

        # Add Button
        add_btn = FilledButton(text="Add New Password")
        add_btn.bind(on_press=self.open_add_popup)

        # Search
        self.search_input = StyledInput(hint_text="Search by app name")
        self.search_input.size_hint_y = None
        self.search_input.height = dp(50)
        self.search_input.bind(text=self.on_search)

        # List container
        self.list_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=[0, dp(4)]
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3), bar_color=C["accent"])
        scroll.add_widget(self.list_layout)

        wrapper.add_widget(header)
        wrapper.add_widget(self.stats_box)
        wrapper.add_widget(add_btn)
        wrapper.add_widget(self.search_input)
        wrapper.add_widget(scroll)

        root.add_widget(wrapper)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = Window.size

    def _draw_lock_btn(self, btn, *args):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*C["card2"])
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
            Color(*C["accent"])
            Line(
                rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(12)),
                width=dp(1)
            )

    def on_pre_enter(self, *args):
        self.load_passwords()

    def on_search(self, instance, value):
        self.load_passwords(value.strip().lower())

    def get_password_keys(self):
        return [k for k in self.store.keys() if k != "pin"]

    def load_passwords(self, search=""):
        self.list_layout.clear_widgets()

        all_keys = self.get_password_keys()
        filtered_keys = all_keys

        if search:
            filtered_keys = [k for k in all_keys if search in k.lower()]

        self.total_label.text = f"[b]{len(all_keys)}[/b]\nTotal"
        self.showing_label.text = f"[b]{len(filtered_keys)}[/b]\nShowing"

        if not filtered_keys:
            empty = Label(
                text="No passwords found",
                font_size=sp(15),
                color=C["hint"],
                size_hint_y=None,
                height=dp(120)
            )
            self.list_layout.add_widget(empty)
            return

        for key in sorted(filtered_keys):
            data = self.store.get(key)
            card = self.make_password_card(
                app_name=key,
                username=data.get("username", ""),
                password=data.get("password", ""),
                timestamp=data.get("timestamp", "")
            )
            self.list_layout.add_widget(card)

    def make_password_card(self, app_name, username, password, timestamp):
        card = RoundedBox(
            bg_color=C["card"],
            radius=14,
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=[dp(16), dp(12)],
            spacing=dp(5)
        )

        # row 1
        row1 = BoxLayout(size_hint_y=None, height=dp(28))
        name_label = Label(
            text=app_name,
            font_size=sp(17),
            bold=True,
            color=C["text"],
            halign="left",
            text_size=(dp(220), None)
        )
        del_btn = Button(
            text="DELETE",
            size_hint_x=None,
            width=dp(72),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=C["red"],
            bold=True,
            font_size=sp(12)
        )
        del_btn.bind(on_press=lambda x, k=app_name: self.confirm_delete(k))
        row1.add_widget(name_label)
        row1.add_widget(del_btn)

        # row 2
        row2 = Label(
            text=f"Username: {username}",
            font_size=sp(13),
            color=C["subtext"],
            halign="left",
            text_size=(dp(300), None),
            size_hint_y=None,
            height=dp(22)
        )

        # row 3
        row3 = BoxLayout(size_hint_y=None, height=dp(30))
        masked = "*" * min(len(password), 12)
        password_label = Label(
            text=f"Password: {masked}",
            font_size=sp(13),
            color=C["subtext"],
            halign="left",
            text_size=(dp(170), None)
        )

        state = {"show": False, "text": password, "label": password_label}

        show_btn = Button(
            text="SHOW",
            size_hint_x=None,
            width=dp(56),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=C["accent"],
            bold=True,
            font_size=sp(12)
        )
        show_btn.bind(on_press=lambda x, s=state, b=show_btn: self.toggle_password(s, b))

        copy_btn = Button(
            text="COPY",
            size_hint_x=None,
            width=dp(56),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=C["green"],
            bold=True,
            font_size=sp(12)
        )
        copy_btn.bind(on_press=lambda x, p=password: self.copy_password(p))

        row3.add_widget(password_label)
        row3.add_widget(show_btn)
        row3.add_widget(copy_btn)

        # row 4
        row4 = Label(
            text=timestamp,
            font_size=sp(11),
            color=C["hint"],
            halign="left",
            text_size=(dp(300), None),
            size_hint_y=None,
            height=dp(18)
        )

        card.add_widget(row1)
        card.add_widget(row2)
        card.add_widget(row3)
        card.add_widget(row4)
        return card

    def toggle_password(self, state, button):
        state["show"] = not state["show"]
        if state["show"]:
            state["label"].text = f"Password: {state['text']}"
            button.text = "HIDE"
        else:
            state["label"].text = f"Password: {'*' * min(len(state['text']), 12)}"
            button.text = "SHOW"

    def copy_password(self, password):
        try:
            Clipboard.copy(password)
            self.show_toast("Password copied")
        except Exception:
            self.show_toast("Copy failed")

    def open_add_popup(self, *args):
        root = RoundedBox(
            bg_color=C["card2"],
            radius=18,
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        title = Label(
            text="Add Password",
            font_size=sp(20),
            bold=True,
            color=C["text"],
            size_hint_y=None,
            height=dp(30)
        )

        self.input_app = StyledInput(hint_text="App or Website Name")
        self.input_app.size_hint_y = None
        self.input_app.height = dp(50)

        self.input_user = StyledInput(hint_text="Username or Email")
        self.input_user.size_hint_y = None
        self.input_user.height = dp(50)

        self.input_pass = StyledInput(hint_text="Password")
        self.input_pass.password = True
        self.input_pass.size_hint_y = None
        self.input_pass.height = dp(50)

        gen_btn = OutlineButton(text="Generate Strong Password")
        gen_btn.bind(on_press=self.generate_password)

        self.popup_error = Label(
            text="",
            font_size=sp(12),
            color=C["red"],
            size_hint_y=None,
            height=dp(18)
        )

        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        cancel_btn = OutlineButton(text="Cancel")
        save_btn = FilledButton(text="Save")

        cancel_btn.bind(on_press=lambda x: self.add_popup.dismiss())
        save_btn.bind(on_press=self.save_password)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)

        root.add_widget(title)
        root.add_widget(self.input_app)
        root.add_widget(self.input_user)
        root.add_widget(self.input_pass)
        root.add_widget(gen_btn)
        root.add_widget(self.popup_error)
        root.add_widget(Widget())
        root.add_widget(btn_row)

        self.add_popup = Popup(
            title="",
            separator_height=0,
            content=root,
            size_hint=(0.9, 0.72),
            background="",
            background_color=(0, 0, 0, 0.7),
            auto_dismiss=True
        )
        self.add_popup.open()

    def generate_password(self, *args):
        chars = string.ascii_letters + string.digits + "!@#$%&*?"
        self.input_pass.text = "".join(random.choice(chars) for _ in range(16))
        self.input_pass.password = False

    def save_password(self, *args):
        app_name = self.input_app.text.strip()
        username = self.input_user.text.strip()
        password = self.input_pass.text.strip()

        if not app_name:
            self.popup_error.text = "App name is required"
            return
        if not username:
            self.popup_error.text = "Username is required"
            return
        if not password:
            self.popup_error.text = "Password is required"
            return

        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.store.put(
            app_name,
            username=username,
            password=password,
            timestamp=timestamp
        )

        self.add_popup.dismiss()
        self.load_passwords()
        self.show_toast("Password saved")

    def confirm_delete(self, key):
        root = RoundedBox(
            bg_color=C["card2"],
            radius=18,
            orientation="vertical",
            padding=dp(18),
            spacing=dp(14)
        )

        root.add_widget(Label(
            text="Delete Password?",
            font_size=sp(18),
            bold=True,
            color=C["text"],
            size_hint_y=None,
            height=dp(28)
        ))
        root.add_widget(Label(
            text=f"This will permanently delete:\n{key}",
            font_size=sp(13),
            color=C["subtext"]
        ))

        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        cancel_btn = OutlineButton(text="Cancel")
        delete_btn = FilledButton(text="Delete", bg_color=C["red"])

        popup_ref = Popup(
            title="",
            separator_height=0,
            content=root,
            size_hint=(0.82, 0.36),
            background="",
            background_color=(0, 0, 0, 0.7),
            auto_dismiss=True
        )

        cancel_btn.bind(on_press=lambda x: popup_ref.dismiss())

        def do_delete(instance):
            self.store.delete(key)
            popup_ref.dismiss()
            self.load_passwords()
            self.show_toast("Deleted")

        delete_btn.bind(on_press=do_delete)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(delete_btn)
        root.add_widget(btn_row)

        popup_ref.open()

    def lock_vault(self, *args):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "pin"

    def show_toast(self, message):
        toast_wrap = FloatLayout(size_hint=(1, 1))

        bg = BoxLayout(
            size_hint=(0.62, None),
            height=dp(42),
            pos_hint={"center_x": 0.5, "y": 0.04}
        )

        with bg.canvas.before:
            Color(*C["green"])
            rect = RoundedRectangle(pos=bg.pos, size=bg.size, radius=[dp(20)])

        bg.bind(
            pos=lambda *a: setattr(rect, "pos", bg.pos),
            size=lambda *a: setattr(rect, "size", bg.size)
        )

        text = Label(
            text=message,
            font_size=sp(13),
            color=C["text"],
            size_hint=(0.62, None),
            height=dp(42),
            pos_hint={"center_x": 0.5, "y": 0.04}
        )

        toast_wrap.add_widget(bg)
        toast_wrap.add_widget(text)
        self.add_widget(toast_wrap)

        Clock.schedule_once(lambda dt: self.remove_widget(toast_wrap), 2)


# ─────────────────────────────────────
# APP
# ─────────────────────────────────────
class SecureVault(App):
    def build(self):
        self.title = "Secure Vault"
        Window.clearcolor = C["bg"]

        try:
            from android.storage import app_storage_path
            store_file = os.path.join(app_storage_path(), "vault.json")
        except Exception:
            store_file = "vault.json"

        self.store = JsonStore(store_file)

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(PinScreen(store=self.store, name="pin"))
        sm.add_widget(MainScreen(store=self.store, name="main"))
        return sm


if __name__ == "__main__":
    SecureVault().run()

Full code
