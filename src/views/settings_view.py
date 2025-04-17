"""
Settings view screen for the reMarkable Agenda Generator.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class SettingsView(Screen):
    """Settings view screen."""
    
    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        
        # Create a simple placeholder layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(
            text="Settings View\n(Implementation in progress)", 
            font_size=24
        ))
        
        self.add_widget(layout)
