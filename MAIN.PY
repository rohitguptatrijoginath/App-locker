from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.metrics import dp

store = JsonStore("vault.json")


class SecureVault(App):

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self.root_layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        self.show_pin_screen()
        return self.root_layout

    # ✅ PIN SCREEN
    def show_pin_screen(self):
        self.root_layout.clear_widgets()

        self.pin_input = TextInput(password=True, multiline=False, hint_text="Enter PIN")
        btn = Button(text="Continue")
        btn.bind(on_press=self.verify_pin)

        self.root_layout.add_widget(Label(text="Secure Vault", font_size='28sp'))
        self.root_layout.add_widget(self.pin_input)
        self.root_layout.add_widget(btn)

    def verify_pin(self, instance):
        pin = self.pin_input.text

        if store.exists("pin"):
            if pin == store.get("pin")["value"]:
                self.show_main_screen()
            else:
                self.pin_input.text = ""
                self.pin_input.hint_text = "Wrong PIN"
        else:
            if pin:
                store.put("pin", value=pin)
                self.show_main_screen()

    # ✅ MAIN SCREEN
    def show_main_screen(self):
        self.root_layout.clear_widgets()

        layout = BoxLayout(orientation="vertical", spacing=dp(10))

        self.app_input = TextInput(hint_text="App Name", multiline=False)
        self.user_input = TextInput(hint_text="Username", multiline=False)
        self.pass_input = TextInput(hint_text="Password", multiline=False, password=True)

        save_btn = Button(text="Save Password")
        save_btn.bind(on_press=self.save_password)

        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.list_layout)

        layout.add_widget(self.app_input)
        layout.add_widget(self.user_input)
        layout.add_widget(self.pass_input)
        layout.add_widget(save_btn)
        layout.add_widget(scroll)

        self.root_layout.add_widget(layout)

        self.load_passwords()

    def save_password(self, instance):
        app = self.app_input.text
        user = self.user_input.text
        pwd = self.pass_input.text

        if app and user and pwd:
            store.put(app, username=user, password=pwd)
            self.app_input.text = ""
            self.user_input.text = ""
            self.pass_input.text = ""
            self.load_passwords()

    def load_passwords(self):
        self.list_layout.clear_widgets()

        for key in store.keys():
            if key != "pin":
                data = store.get(key)
                text = f"{key} | {data['username']} | {data['password']}"
                btn = Button(text=text, size_hint_y=None, height=dp(40))
                btn.bind(on_press=lambda x, k=key: self.delete_entry(k))
                self.list_layout.add_widget(btn)

    def delete_entry(self, key):
        store.delete(key)
        self.load_passwords()


if __name__ == "__main__":
    SecureVault().run()
