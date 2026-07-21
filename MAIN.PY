import os
import json
import base64
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Soft background color
Window.clearcolor = (0.95, 0.95, 0.97, 1)

DATA_FILE = "vault_data.json"

def obfuscate_data(data_str):
    """Simple encoding for local storage demo (Not military encryption)"""
    return base64.b64encode(data_str.encode('utf-8')).decode('utf-8')

def deobfuscate_data(data_str):
    """Simple decoding for local storage demo"""
    try:
        return base64.b64decode(data_str.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        layout.add_widget(Label(
            text="[b]Secure Vault[/b]", 
            markup=True, 
            font_size='28sp', 
            color=(0.1, 0.1, 0.2, 1)
        ))
        
        layout.add_widget(Label(
            text="Enter PIN / Passcode:", 
            font_size='16sp', 
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        self.pin_input = TextInput(
            password=True, 
            multiline=False, 
            font_size='18sp', 
            size_hint_y=None, 
            height=50
        )
        layout.add_widget(self.pin_input)
        
        btn_login = Button(
            text="Unlock Vault", 
            size_hint_y=None, 
            height=50, 
            background_color=(0.2, 0.6, 0.8, 1)
        )
        btn_login.bind(on_press=self.verify_pin)
        layout.add_widget(btn_login)
        
        self.add_widget(layout)

    def verify_pin(self, instance):
        pin = self.pin_input.text.strip()
        if not pin:
            self.show_popup("Error", "Please enter a PIN.")
            return
        
        # Simple local pin validation
        if not os.path.exists(DATA_FILE):
            # First time user setup
            with open(DATA_FILE, "w") as f:
                json.dump({"pin": obfuscate_data(pin), "items": []}, f)
            self.manager.current = 'vault'
        else:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            saved_pin = deobfuscate_data(data.get("pin", ""))
            if pin == saved_pin:
                self.pin_input.text = ""
                self.manager.current = 'vault'
            else:
                self.show_popup("Access Denied", "Incorrect PIN!")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()


class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        header.add_widget(Label(
            text="[b]My Vault Items[/b]", 
            markup=True, 
            font_size='20sp', 
            color=(0.1, 0.1, 0.2, 1)
        ))
        btn_logout = Button(text="Lock", size_hint_x=None, width=80)
        btn_logout.bind(on_press=self.logout)
        header.add_widget(btn_logout)
        self.layout.add_widget(header)
        
        # Add Item Inputs
        input_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=110)
        self.title_input = TextInput(hint_text="Title (e.g. Note / Password)", multiline=False)
        self.content_input = TextInput(hint_text="Secret Content", multiline=False)
        input_box.add_widget(self.title_input)
        input_box.add_widget(self.content_input)
        self.layout.add_widget(input_box)
        
        btn_add = Button(text="Add to Vault", size_hint_y=None, height=45, background_color=(0.2, 0.7, 0.3, 1))
        btn_add.bind(on_press=self.add_item)
        self.layout.add_widget(btn_add)
        
        # Items List View
        self.scroll = ScrollView()
        self.items_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.items_list.bind(minimum_height=self.items_list.setter('height'))
        self.scroll.add_widget(self.items_list)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.load_items()

    def load_items(self):
        self.items_list.clear_widgets()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            items = data.get("items", [])
            for idx, item in enumerate(items):
                title = deobfuscate_data(item.get("title", ""))
                val = deobfuscate_data(item.get("value", ""))
                
                card = BoxLayout(orientation='vertical', padding=10, size_hint_y=None, height=70)
                card.add_widget(Label(
                    text=f"[b]{title}[/b]: {val}", 
                    markup=True, 
                    color=(0.2, 0.2, 0.2, 1)
                ))
                self.items_list.add_widget(card)

    def add_item(self, instance):
        t = self.title_input.text.strip()
        v = self.content_input.text.strip()
        if not t or not v:
            return
        
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            
            data["items"].append({
                "title": obfuscate_data(t),
                "value": obfuscate_data(v)
            })
            
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
                
            self.title_input.text = ""
            self.content_input.text = ""
            self.load_items()

    def logout(self, instance):
        self.manager.current = 'login'


class SecureVaultApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(VaultScreen(name='vault'))
        return sm


if __name__ == '__main__':
    SecureVaultApp().run()

