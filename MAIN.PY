"""
AppLock Application - Main Module
This application provides multiple authentication methods for securing other apps.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
import hashlib
import json
import os

# Try to import Pyjnius for Android features
try:
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.USE_BIOMETRIC, Permission.USE_FINGERPRINT])
    # Initialize Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    BiometricPrompt = autoclass('android.hardware.biometrics.BiometricPrompt')
    BiometricPromptBuilder = autoclass('android.hardware.biometrics.BiometricPrompt$Builder')
    CancellationSignal = autoclass('android.os.CancellationSignal')
    Executor = autoclass('java.util.concurrent.Executors').newSingleThreadExecutor()
except ImportError:
    print("Pyjnius not available - running in desktop mode")

class PatternWidget(Widget):
    def __init__(self, **kwargs):
        super(PatternWidget, self).__init__(**kwargs)
        self.dots = []
        self.selected_dots = []
        self.dot_positions = []
        self.setup_pattern()
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def setup_pattern(self):
        # Create 9 dots in 3x3 grid
        for row in range(3):
            for col in range(3):
                x = self.x + (col * 100) + 50
                y = self.y + (row * 100) + 50
                self.dot_positions.append((x, y))
        
    def update_graphics(self, *args):
        self.canvas.clear()
        if not self.dot_positions:
            return
        
        # Recalculate positions based on current widget size
        padding = 40
        spacing_x = (self.width - (padding * 2)) / 2
        spacing_y = (self.height - (padding * 2)) / 2
        
        for i in range(3):
            for j in range(3):
                x = self.x + padding + (j * spacing_x)
                y = self.y + padding + (i * spacing_y)
                
                with self.canvas:
                    if i*3+j in [dot_idx for dot_idx, _ in self.selected_dots]:
                        Color(0, 0.7, 1, 1)  # Selected color
                    else:
                        Color(0.8, 0.8, 0.8, 1)  # Default color
                    Ellipse(pos=(x-15, y-15), size=(30, 30))
                    
                    # Draw connecting lines between selected dots
                    if len(self.selected_dots) > 1:
                        for idx in range(len(self.selected_dots)-1):
                            start_pos = self.selected_dots[idx][1]
                            end_pos = self.selected_dots[idx+1][1]
                            
                            Color(0, 0.7, 1, 1)
                            Line(points=[start_pos[0], start_pos[1], end_pos[0], end_pos[1]], width=4)
    
    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        self.check_dot_collision(touch)
        return True
    
    def on_touch_move(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        self.check_dot_collision(touch)
        self.update_graphics()
    
    def on_touch_up(self, touch):
        pattern_result = [idx for idx, pos in self.selected_dots]
        self.parent.pattern_completed(pattern_result)
        self.reset_pattern()
    
    def check_dot_collision(self, touch):
        padding = 40
        spacing_x = (self.width - (padding * 2)) / 2
        spacing_y = (self.height - (padding * 2)) / 2
        
        for i in range(3):
            for j in range(3):
                x = self.x + padding + (j * spacing_x)
                y = self.y + padding + (i * spacing_y)
                
                distance = ((touch.x - x)**2 + (touch.y - y)**2)**0.5
                if distance < 30 and (i*3+j) not in [dot_idx for dot_idx, _ in self.selected_dots]:
                    self.selected_dots.append((i*3+j, (x, y)))
                    break
    
    def reset_pattern(self):
        self.selected_dots = []
        self.update_graphics()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(text='AppLock Security', font_size=30, size_hint_y=None, height=50)
        layout.add_widget(title)
        
        btn_layout = GridLayout(cols=2, spacing=20, size_hint_y=None, height=300)
        
        pin_btn = Button(text='PIN Lock', font_size=18)
        pin_btn.bind(on_press=lambda x: self.manager.current = 'pin_setup')
        btn_layout.add_widget(pin_btn)
        
        password_btn = Button(text='Password Lock', font_size=18)
        password_btn.bind(on_press=lambda x: self.manager.current = 'password_setup')
        btn_layout.add_widget(password_btn)
        
        pattern_btn = Button(text='Pattern Lock', font_size=18)
        pattern_btn.bind(on_press=lambda x: self.manager.current = 'pattern_setup')
        btn_layout.add_widget(pattern_btn)
        
        fingerprint_btn = Button(text='Fingerprint Lock', font_size=18)
        fingerprint_btn.bind(on_press=lambda x: self.authenticate_fingerprint())
        btn_layout.add_widget(fingerprint_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def authenticate_fingerprint(self):
        try:
            # Android fingerprint authentication
            activity = PythonActivity.mActivity
            executor = Executor
            
            biometric_prompt = BiometricPromptBuilder(activity).apply {
                setTitle('Fingerprint Authentication')
                setSubtitle('Unlock with your fingerprint')
                setDescription('Place your finger on the sensor')
                setNegativeButton('Cancel', executor, lambda cancelled: print("Cancelled"))
            }.build()
            
            authentication_callback = autoclass('android.hardware.biometrics.BiometricPrompt$AuthenticationCallback')()
            biometric_prompt.authenticate(CancellationSignal(), executor, authentication_callback)
            
            popup = Popup(title='Success', content=Label(text='Fingerprint authenticated!'), size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Fingerprint not available: {str(e)}'), size_hint=(0.8, 0.4))
            popup.open()

class PinSetupScreen(Screen):
    def __init__(self, **kwargs):
        super(PinSetupScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(text='Set PIN Code', font_size=25, size_hint_y=None, height=50)
        layout.add_widget(title)
        
        self.pin_input = TextInput(hint_text='Enter 4-digit PIN', password=True, input_filter='int', 
                                  multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.pin_input)
        
        confirm_pin = TextInput(hint_text='Confirm PIN', password=True, input_filter='int',
                               multiline=False, size_hint_y=None, height=50)
        layout.add_widget(confirm_pin)
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        save_btn = Button(text='Save PIN')
        save_btn.bind(on_press=lambda x: self.save_pin(self.pin_input.text, confirm_pin.text))
        btn_layout.add_widget(save_btn)
        
        back_btn = Button(text='Back')
        back_btn.bind(on_press=lambda x: self.manager.current = 'home')
        btn_layout.add_widget(back_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def save_pin(self, pin, confirm_pin):
        if len(pin) != 4:
            popup = Popup(title='Error', content=Label(text='PIN must be 4 digits'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        if pin != confirm_pin:
            popup = Popup(title='Error', content=Label(text='PINs do not match'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        # Save hashed PIN
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        with open('lock_config.json', 'w') as f:
            json.dump({'pin': hashed_pin, 'method': 'pin'}, f)
        
        popup = Popup(title='Success', content=Label(text='PIN saved successfully!'), size_hint=(0.8, 0.4))
        popup.open()
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'home'), 1.5)

class PasswordSetupScreen(Screen):
    def __init__(self, **kwargs):
        super(PasswordSetupScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(text='Set Password', font_size=25, size_hint_y=None, height=50)
        layout.add_widget(title)
        
        self.password_input = TextInput(hint_text='Enter Password', password=True,
                                       multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.password_input)
        
        confirm_password = TextInput(hint_text='Confirm Password', password=True,
                                    multiline=False, size_hint_y=None, height=50)
        layout.add_widget(confirm_password)
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        save_btn = Button(text='Save Password')
        save_btn.bind(on_press=lambda x: self.save_password(self.password_input.text, confirm_password.text))
        btn_layout.add_widget(save_btn)
        
        back_btn = Button(text='Back')
        back_btn.bind(on_press=lambda x: self.manager.current = 'home')
        btn_layout.add_widget(back_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def save_password(self, password, confirm_password):
        if len(password) < 4:
            popup = Popup(title='Error', content=Label(text='Password must be at least 4 characters'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        if password != confirm_password:
            popup = Popup(title='Error', content=Label(text='Passwords do not match'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        # Save hashed password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with open('lock_config.json', 'w') as f:
            json.dump({'password': hashed_password, 'method': 'password'}, f)
        
        popup = Popup(title='Success', content=Label(text='Password saved successfully!'), size_hint=(0.8, 0.4))
        popup.open()
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'home'), 1.5)

class PatternSetupScreen(Screen):
    def __init__(self, **kwargs):
        super(PatternSetupScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(text='Draw Unlock Pattern', font_size=25, size_hint_y=None, height=50)
        layout.add_widget(title)
        
        instruction = Label(text='Connect at least 4 dots in any order', size_hint_y=None, height=30)
        layout.add_widget(instruction)
        
        self.pattern_widget = PatternWidget(size_hint_y=3)
        layout.add_widget(self.pattern_widget)
        
        self.confirm_pattern = None
        self.pattern_phase = 'setup'  # 'setup' or 'confirm'
        
        status_label = Label(text='Draw your pattern', size_hint_y=None, height=30)
        self.status_label = status_label
        layout.add_widget(status_label)
        
        back_btn = Button(text='Back', size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: self.manager.current = 'home')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def pattern_completed(self, pattern):
        if self.pattern_phase == 'setup':
            if len(pattern) < 4:
                self.status_label.text = 'Pattern too short! Use at least 4 dots'
                return
            
            self.confirm_pattern = pattern
            self.pattern_phase = 'confirm'
            self.status_label.text = 'Draw the same pattern again to confirm'
        else:  # confirmation phase
            if pattern == self.confirm_pattern:
                # Save pattern
                pattern_str = ','.join(map(str, pattern))
                hashed_pattern = hashlib.sha256(pattern_str.encode()).hexdigest()
                with open('lock_config.json', 'w') as f:
                    json.dump({'pattern': hashed_pattern, 'method': 'pattern'}, f)
                
                self.status_label.text = 'Pattern saved successfully!'
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'home'), 1.5)
            else:
                self.status_label.text = 'Patterns do not match! Try again'
                self.pattern_phase = 'setup'

class AppLockApp(App):
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(PinSetupScreen(name='pin_setup'))
        sm.add_widget(PasswordSetupScreen(name='password_setup'))
        sm.add_widget(PatternSetupScreen(name='pattern_setup'))
        
        # Set window size for development
        Window.size = (400, 600)
        
        return sm

if __name__ == '__main__':
    AppLockApp().run()
