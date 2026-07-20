import os
import hashlib
import string
import random
import json
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
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from functools import partial


# ═══════════════════════════════════════
# COLORS
# ═══════════════════════════════════════
C = {
    'bg':         get_color_from_hex('#0A0E27'),
    'card':       get_color_from_hex('#1A2040'),
    'accent':     get_color_from_hex('#6C63FF'),
    'accent2':    get_color_from_hex('#5A52E0'),
    'green':      get_color_from_hex('#00D68F'),
    'red':        get_color_from_hex('#FF3D71'),
    'white':      get_color_from_hex('#FFFFFF'),
    'grey':       get_color_from_hex('#8F9BB3'),
    'dark_grey':  get_color_from_hex('#5A6380'),
    'input_bg':   get_color_from_hex('#1E2548'),
    'border':     get_color_from_hex('#2E3663'),
}


# ═══════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════
class RBox(BoxLayout):
    def __init__(self, bg=None, r=16, **kw):
        super().__init__(**kw)
        self._bg = bg or C['card']
        self._r = r
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self._r)])


class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = C['white']
        self.cursor_color = C['accent']
        self.hint_text_color = C['dark_grey']
        self.font_size = sp(16)
        self.padding = [dp(18), dp(14), dp(18), dp(14)]
        self.multiline = False
        self.bind(pos=self._draw, size=self._draw, focus=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *a):
        self.canvas.before.clear()
        bc = C['accent'] if self.focus else C['border']
        with self.canvas.before:
            Color(*C['input_bg'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*bc)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                 width=dp(1.5) if self.focus else dp(1))


class PBtn(Button):
    def __init__(self, bg=None, **kw):
        super().__init__(**kw)
        self._bg = bg or C['accent']
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = C['white']
        self.font_size = sp(16)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(52)
        self.bind(pos=self._draw, size=self._draw, state=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *a):
        self.canvas.before.clear()
        c = C['accent2'] if self.state == 'down' else self._bg
        with self.canvas.before:
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class OBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = C['accent']
        self.font_size = sp(15)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(lambda dt: self._draw())

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C['card'])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*C['accent'])
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                 width=dp(1.5))


# ═══════════════════════════════════════
# SPLASH SCREEN
# ═══════════════════════════════════════
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = FloatLayout()

        with self.layout.canvas.before:
            Color(*C['bg'])
            self._rect = Rectangle(pos=(0, 0), size=Window.size)

        from kivy.graphics import Rectangle
        with self.layout.canvas.before:
            Color(*C['bg'])
            self._rect = Rectangle(pos=(0, 0), size=Window.size)
        self.layout.bind(size=lambda *a: setattr(self._rect, 'size', Window.size))

        box = BoxLayout(orientation='vertical',
                        size_hint=(0.7, 0.35),
                        pos_hint={'center_x': 0.5, 'center_y': 0.55},
                        spacing=dp(8))

        box.add_widget(Label(text='\U0001F6E1', font_size=sp(64)))
        box.add_widget(Label(text='Secure Vault', font_size=sp(30),
                             bold=True, color=C['white']))
        box.add_widget(Label(text='Your passwords, protected.',
                             font_size=sp(14), color=C['grey']))

        self.layout.add_widget(box)
        self.layout.add_widget(
            Label(text='v1.0', font_size=sp(11), color=C['dark_grey'],
                  size_hint=(1, 0.05), pos_hint={'center_x': 0.5, 'y': 0.03})
        )
        self.add_widget(self.layout)

    def on_enter(self):
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'pin'), 2)


# ═══════════════════════════════════════
# PIN SCREEN
# ═══════════════════════════════════════
class PinScreen(Screen):
    def __init__(self, store, **kw):
        super().__init__(**kw)
        self.store = store
        self.pin = ""
        self.is_new = not store.exists("pin")

        root = FloatLayout()
        with root.canvas.before:
            Color(*C['bg'])
            self._r = Rectangle(pos=(0, 0), size=Window.size)

        from kivy.graphics import Rectangle
        with root.canvas.before:
            Color(*C['bg'])
            self._r = Rectangle(pos=(0, 0), size=Window.size)
        root.bind(size=lambda *a: setattr(self._r, 'size', Window.size))

        content = BoxLayout(orientation='vertical',
                            size_hint=(0.85, 0.92),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            spacing=dp(8))

        content.add_widget(Widget(size_hint_y=0.06))
        content.add_widget(Label(text='\U0001F512', font_size=sp(52), size_hint_y=0.1))

        self.title_l = Label(
            text='Create PIN' if self.is_new else 'Enter PIN',
            font_size=sp(24), bold=True, color=C['white'], size_hint_y=0.06)

        self.sub_l = Label(
            text='Set a 4-digit PIN' if self.is_new else 'Enter your PIN to unlock',
            font_size=sp(13), color=C['grey'], size_hint_y=0.04)

        # Dots
        self.dots_box = BoxLayout(size_hint=(0.4, 0.05),
                                  pos_hint={'center_x': 0.5}, spacing=dp(16))
        self.dots = []
        for _ in range(4):
            d = Label(text='\u25CB', font_size=sp(26), color=C['dark_grey'])
            self.dots.append(d)
            self.dots_box.add_widget(d)

        self.err = Label(text='', font_size=sp(13), color=C['red'], size_hint_y=0.04)

        content.add_widget(self.title_l)
        content.add_widget(self.sub_l)
        content.add_widget(Widget(size_hint_y=0.02))
        content.add_widget(self.dots_box)
        content.add_widget(self.err)
        content.add_widget(Widget(size_hint_y=0.02))

        # Numpad
        pad = GridLayout(cols=3, size_hint=(0.82, 0.45),
                         pos_hint={'center_x': 0.5}, spacing=dp(10))

        for t in ['1','2','3','4','5','6','7','8','9','','0','\u232B']:
            if t == '':
                pad.add_widget(Widget())
            else:
                b = Button(text=t, font_size=sp(24), bold=True,
                           background_color=(0,0,0,0), background_normal='',
                           color=C['white'])
                b.bind(pos=self._draw_pad, size=self._draw_pad)
                Clock.schedule_once(partial(self._init_pad, b), 0.1)
                if t == '\u232B':
                    b.bind(on_press=self._back)
                else:
                    b.bind(on_press=self._press)
                pad.add_widget(b)

        content.add_widget(pad)
        root.add_widget(content)
        self.add_widget(root)

    def on_enter(self):
        self.pin = ""
        self.is_new = not self.store.exists("pin")
        self.title_l.text = 'Create PIN' if self.is_new else 'Enter PIN'
        self.sub_l.text = 'Set a 4-digit PIN' if self.is_new else 'Enter your PIN to unlock'
        self.err.text = ''
        self._upd_dots()

    def _init_pad(self, btn, dt):
        self._draw_pad(btn)

    def _draw_pad(self, btn, *a):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*C['card'])
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(40)])

    def _press(self, inst):
        if len(self.pin) < 4:
            self.pin += inst.text
            self._upd_dots()
            if len(self.pin) == 4:
                Clock.schedule_once(self._verify, 0.2)

    def _back(self, *a):
        if self.pin:
            self.pin = self.pin[:-1]
            self._upd_dots()
            self.err.text = ''

    def _upd_dots(self):
        for i in range(4):
            if i < len(self.pin):
                self.dots[i].text = '\u25CF'
                self.dots[i].color = C['accent']
            else:
                self.dots[i].text = '\u25CB'
                self.dots[i].color = C['dark_grey']

    def _verify(self, dt):
        p = self.pin
        if self.is_new:
            h = hashlib.sha256(p.encode()).hexdigest()
            self.store.put("pin", value=h)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'main'
        else:
            stored = self.store.get("pin")["value"]
            if hashlib.sha256(p.encode()).hexdigest() == stored:
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = 'main'
            else:
                self.err.text = 'Wrong PIN. Try again.'
                self.pin = ""
                self._upd_dots()
                # Shake animation
                ox = self.dots_box.x
                anim = (Animation(x=ox - dp(10), d=0.05) +
                        Animation(x=ox + dp(10), d=0.05) +
                        Animation(x=ox, d=0.05))
                anim.start(self.dots_box)


# ═══════════════════════════════════════
# MAIN SCREEN
# ═══════════════════════════════════════
class MainScreen(Screen):
    def __init__(self, store, **kw):
        super().__init__(**kw)
        self.store = store

        root = FloatLayout()
        with root.canvas.before:
            Color(*C['bg'])
            self._r = Rectangle(pos=(0, 0), size=Window.size)

        from kivy.graphics import Rectangle
        with root.canvas.before:
            Color(*C['bg'])
            self._r = Rectangle(pos=(0, 0), size=Window.size)
        root.bind(size=lambda *a: setattr(self._r, 'size', Window.size))

        content = BoxLayout(orientation='vertical',
                            size_hint=(0.92, 0.96),
                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            spacing=dp(10))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(50))
        hdr.add_widget(Label(text='\U0001F6E1  Secure Vault', font_size=sp(22),
                             bold=True, color=C['white'], halign='left',
                             text_size=(dp(250), None)))

        lock_btn = Button(text='\U0001F512', size_hint_x=None, width=dp(48),
                          background_color=(0,0,0,0), background_normal='',
                          font_size=sp(22), color=C['grey'])
        lock_btn.bind(on_press=self._lock)
        hdr.add_widget(lock_btn)

        # Stats
        self.stats = RBox(bg=C['card'], r=14, size_hint_y=None, height=dp(55),
                          padding=[dp(20), dp(8)], spacing=dp(10))
        self.total_l = Label(text='0\nTotal', font_size=sp(13),
                             color=C['white'], halign='center', markup=True)
        self.show_l = Label(text='0\nShowing', font_size=sp(13),
                            color=C['accent'], halign='center', markup=True)
        self.stats.add_widget(self.total_l)
        self.stats.add_widget(self.show_l)

        # Add button
        add_btn = PBtn(text='\u2795  Add New Password')
        add_btn.bind(on_press=self._show_add)

        # Search
        self.search = SInput(hint_text='\U0001F50D  Search...')
        self.search.size_hint_y = None
        self.search.height = dp(48)
        self.search.bind(text=self._on_search)

        # List
        self.list_box = GridLayout(cols=1, size_hint_y=None,
                                   spacing=dp(10), padding=[0, dp(6)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(2),
                            bar_color=C['accent'])
        scroll.add_widget(self.list_box)

        content.add_widget(hdr)
        content.add_widget(self.stats)
        content.add_widget(add_btn)
        content.add_widget(self.search)
        content.add_widget(scroll)

        root.add_widget(content)
        self.add_widget(root)

    def on_enter(self):
        self._load()

    def _on_search(self, inst, val):
        self._load(val.strip().lower())

    def _load(self, search=""):
        self.list_box.clear_widgets()
        keys = [k for k in self.store.keys() if k != "pin"]
        if search:
            keys = [k for k in keys if search in k.lower()]

        total = len([k for k in self.store.keys() if k != "pin"])
        self.total_l.text = f'[b]{total}[/b]\nTotal'
        self.show_l.text = f'[b]{len(keys)}[/b]\nShowing'

        if not keys:
            self.list_box.add_widget(
                Label(text='\U0001F4AD\n\nNo passwords found',
                      font_size=sp(15), color=C['dark_grey'],
                      halign='center', size_hint_y=None, height=dp(120)))
            return

        for key in sorted(keys):
            d = self.store.get(key)
            card = self._make_card(key, d.get('username', ''),
                                   d.get('password', ''),
                                   d.get('timestamp', ''))
            self.list_box.add_widget(card)

    def _make_card(self, name, user, pwd, ts):
        card = RBox(bg=C['card'], r=14, orientation='vertical',
                    size_hint_y=None, height=dp(130),
                    padding=[dp(16), dp(12)], spacing=dp(4))

        # Row 1 - Name + Delete
        r1 = BoxLayout(size_hint_y=None, height=dp(30))
        r1.add_widget(Label(text=f'\U0001F4F1  {name}', font_size=sp(17),
                            bold=True, color=C['white'], halign='left',
                            text_size=(dp(220), None)))
        del_b = Button(text='\u2716', size_hint_x=None, width=dp(36),
                       background_color=(0,0,0,0), background_normal='',
                       font_size=sp(16), color=C['red'])
        del_b.bind(on_press=lambda x, k=name: self._confirm_del(k))
        r1.add_widget(del_b)

        # Row 2 - Username
        r2 = Label(text=f'\U0001F464  {user}', font_size=sp(14),
                   color=C['grey'], halign='left',
                   text_size=(dp(300), None), size_hint_y=None, height=dp(22))

        # Row 3 - Password
        r3 = BoxLayout(size_hint_y=None, height=dp(28))
        pwd_l = Label(text=f'\U0001F512  {"*" * min(len(pwd), 10)}',
                      font_size=sp(14), color=C['grey'], halign='left',
                      text_size=(dp(180), None))
        pwd_data = {'show': False, 'pwd': pwd, 'label': pwd_l}

        eye_b = Button(text='\U0001F441', size_hint_x=None, width=dp(36),
                       background_color=(0,0,0,0), background_normal='',
                       font_size=sp(15))
        eye_b.bind(on_press=lambda x, d=pwd_data: self._toggle_pwd(d))

        copy_b = Button(text='Copy', size_hint_x=None, width=dp(60),
                        background_color=(0,0,0,0), background_normal='',
                        font_size=sp(13), color=C['accent'])
        copy_b.bind(on_press=lambda x, p=pwd: self._copy(p))

        r3.add_widget(pwd_l)
        r3.add_widget(eye_b)
        r3.add_widget(copy_b)

        # Row 4 - Time
        r4 = Label(text=f'  {ts}', font_size=sp(11), color=C['dark_grey'],
                   halign='left', text_size=(dp(300), None),
                   size_hint_y=None, height=dp(18))

        card.add_widget(r1)
        card.add_widget(r2)
        card.add_widget(r3)
        card.add_widget(r4)
        return card

    def _toggle_pwd(self, data):
        data['show'] = not data['show']
        if data['show']:
            data['label'].text = f'\U0001F513  {data["pwd"]}'
        else:
            data['label'].text = f'\U0001F512  {"*" * min(len(data["pwd"]), 10)}'

    def _copy(self, text):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self._toast('Copied!')
        except Exception:
            self._toast('Copy failed')

    def _show_add(self, *a):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        self.p_app = SInput(hint_text='App / Website Name')
        self.p_app.size_hint_y = None
        self.p_app.height = dp(50)

        self.p_user = SInput(hint_text='Username / Email')
        self.p_user.size_hint_y = None
        self.p_user.height = dp(50)

        self.p_pwd = SInput(hint_text='Password')
        self.p_pwd.password = True
        self.p_pwd.size_hint_y = None
        self.p_pwd.height = dp(50)

        gen_btn = OBtn(text='\U0001F3B2  Generate Password')
        gen_btn.bind(on_press=self._gen_pwd)

        self.p_err = Label(text='', font_size=sp(12), color=C['red'],
                           size_hint_y=None, height=dp(18))

        btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        c_btn = OBtn(text='Cancel')
        s_btn = PBtn(text='Save')
        c_btn.bind(on_press=lambda x: self.popup.dismiss())
        s_btn.bind(on_press=self._save)
        btns.add_widget(c_btn)
        btns.add_widget(s_btn)

        box.add_widget(Label(text='Add Password', font_size=sp(20),
                             bold=True, color=C['white'],
                             size_hint_y=None, height=dp(32)))
        box.add_widget(self.p_app)
        box.add_widget(self.p_user)
        box.add_widget(self.p_pwd)
        box.add_widget(gen_btn)
        box.add_widget(self.p_err)
        box.add_widget(Widget(size_hint_y=0.1))
        box.add_widget(btns)

        self.popup = Popup(title='', separator_height=0, content=box,
                           size_hint=(0.9, 0.7),
                           background_color=(0, 0, 0, 0.8), background='')
        self.popup.open()

    def _gen_pwd(self, *a):
        ch = string.ascii_letters + string.digits + '!@#$%&*'
        self.p_pwd.text = ''.join(random.choice(ch) for _ in range(16))
        self.p_pwd.password = False

    def _save(self, *a):
        app = self.p_app.text.strip()
        user = self.p_user.text.strip()
        pwd = self.p_pwd.text.strip()

        if not app:
            self.p_err.text = 'App name required'
            return
        if not user:
            self.p_err.text = 'Username required'
            return
        if not pwd:
            self.p_err.text = 'Password required'
            return

        ts = datetime.now().strftime('%d %b %Y, %I:%M %p')
        self.store.put(app, username=user, password=pwd, timestamp=ts)
        self.popup.dismiss()
        self._load()
        self._toast('Saved!')

    def _confirm_del(self, key):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box.add_widget(Label(text='\u26A0', font_size=sp(44), size_hint_y=0.3))
        box.add_widget(Label(text=f'Delete "{key}"?\n\nCannot be undone.',
                             font_size=sp(15), color=C['grey'],
                             halign='center', size_hint_y=0.3))

        btns = BoxLayout(spacing=dp(10), size_hint_y=0.25)
        c = OBtn(text='Cancel')
        d = PBtn(text='Delete', bg=C['red'])

        def do_del(x):
            self.store.delete(key)
            self._load()
            dp2.dismiss()
            self._toast(f'"{key}" deleted')

        c.bind(on_press=lambda x: dp2.dismiss())
        d.bind(on_press=do_del)
        btns.add_widget(c)
        btns.add_widget(d)
        box.add_widget(btns)

        dp2 = Popup(title='', separator_height=0, content=box,
                     size_hint=(0.8, 0.38),
                     background_color=(0, 0, 0, 0.8), background='')
        dp2.open()

    def _lock(self, *a):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'pin'

    def _toast(self, msg):
        t = Label(text=msg, font_size=sp(14), color=C['white'],
                  size_hint=(0.6, None), height=dp(40),
                  pos_hint={'center_x': 0.5, 'y': 0.05})

        bg = BoxLayout(size_hint=(0.6, None), height=dp(40),
                       pos_hint={'center_x': 0.5, 'y': 0.05})
        with bg.canvas.before:
            Color(*C['green'][:3], 0.9)
            r = RoundedRectangle(pos=bg.pos, size=bg.size, radius=[dp(20)])
        bg.bind(pos=lambda *a: setattr(r, 'pos', bg.pos),
                size=lambda *a: setattr(r, 'size', bg.size))

        f = FloatLayout(size_hint=(1, 1))
        f.add_widget(bg)
        f.add_widget(t)
        self.add_widget(f)
        Clock.schedule_once(lambda dt: self.remove_widget(f), 2)


# ═══════════════════════════════════════
# APP
# ═══════════════════════════════════════
class SecureVault(App):
    def build(self):
        self.title = 'Secure Vault'
        Window.clearcolor = C['bg']

        # Use app directory for storage
        try:
            from android.storage import app_storage_path
            store_path = os.path.join(app_storage_path(), 'vault.json')
        except Exception:
            store_path = 'vault.json'

        self.store = JsonStore(store_path)

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(PinScreen(store=self.store, name='pin'))
        sm.add_widget(MainScreen(store=self.store, name='main'))
        return sm


if __name__ == '__main__':
    SecureVault().run()
