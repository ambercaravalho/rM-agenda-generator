"""
Settings view for configuring application preferences.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.settings import SettingsWithSidebar

class SettingsView(Screen):
    """Settings screen for the application."""
    
    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # iCal URL Input
        ical_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        ical_layout.add_widget(Label(text="iCal URL:", size_hint_x=0.3))
        self.ical_input = TextInput(multiline=False, size_hint_x=0.7)
        ical_layout.add_widget(self.ical_input)
        layout.add_widget(ical_layout)
        
        # Weather API Key Input
        weather_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        weather_layout.add_widget(Label(text="Weather API Key:", size_hint_x=0.3))
        self.weather_key_input = TextInput(multiline=False, size_hint_x=0.7)
        weather_layout.add_widget(self.weather_key_input)
        layout.add_widget(weather_layout)
        
        # Location Input
        location_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        location_layout.add_widget(Label(text="Location:", size_hint_x=0.3))
        self.location_input = TextInput(multiline=False, size_hint_x=0.7)
        location_layout.add_widget(self.location_input)
        layout.add_widget(location_layout)
        
        # Save Button
        save_btn = Button(text="Save Settings", size_hint_y=None, height=50)
        save_btn.bind(on_press=self.save_settings)
        layout.add_widget(save_btn)
        
        # Back Button
        back_btn = Button(text="Back to Calendar", size_hint_y=None, height=50)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def save_settings(self, instance):
        """Save the current settings."""
        # Here you would save the settings to a configuration file
        print(f"Saving settings: iCal URL: {self.ical_input.text}, "
              f"Weather API Key: {self.weather_key_input.text}, "
              f"Location: {self.location_input.text}")
    
    def go_back(self, instance):
        """Navigate back to the main screen."""
        self.manager.current = 'main'
