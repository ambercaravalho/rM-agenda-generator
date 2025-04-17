"""
Tablet selection screen for the reMarkable Agenda Generator.
"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

from utils.ui_helpers import SafeLabel

class DeviceButton(BoxLayout):
    """Custom button with image for device selection."""
    
    def __init__(self, text, image_source, callback, **kwargs):
        super(DeviceButton, self).__init__(orientation='vertical', **kwargs)
        self.size_hint = (1, None)
        self.height = dp(250)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Image
        self.image = Image(source=image_source, allow_stretch=True, keep_ratio=True, 
                           size_hint=(1, 0.8))
        self.add_widget(self.image)
        
        # Button
        self.button = Button(text=text, size_hint=(1, 0.2), height=dp(40))
        self.button.bind(on_press=callback)
        self.add_widget(self.button)
        
        # Schedule a delayed reload to ensure images load properly
        Clock.schedule_once(self._reload_image, 0.5)
        
    def _reload_image(self, dt):
        """Reload the image after a delay to ensure it loads properly."""
        if self.image:
            self.image.reload()

class TabletSelectionView(Screen):
    """Tablet selection screen."""
    
    def __init__(self, **kwargs):
        super(TabletSelectionView, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Title
        self.title = SafeLabel(
            text="Select Your reMarkable Tablet Model",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            bold=True,
            halign='center'
        )
        self.layout.add_widget(self.title)
        
        # Description
        self.description = SafeLabel(
            text="Choose your reMarkable tablet model to generate optimized PDFs",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        self.layout.add_widget(self.description)
        
        # Spacer
        self.layout.add_widget(BoxLayout(size_hint_y=0.1))
        
        # Device selection buttons with images
        self.devices_layout = BoxLayout(orientation='horizontal', spacing=dp(30), size_hint_y=None, height=dp(300))
        
        # Get image paths
        image_dir = os.path.join("assets", "images")
        rm1_image = os.path.join(image_dir, "remarkable1.jpg")
        rm2_image = os.path.join(image_dir, "remarkable2.jpg")
        rmpro_image = os.path.join(image_dir, "paperpro.jpg")
        
        # Use default placeholder if images don't exist
        default_image = os.path.join(image_dir, "device_placeholder.png")
        rm1_image = rm1_image if os.path.exists(rm1_image) else default_image
        rm2_image = rm2_image if os.path.exists(rm2_image) else default_image
        rmpro_image = rmpro_image if os.path.exists(rmpro_image) else default_image
        
        # reMarkable 1 button with image
        self.rm1 = DeviceButton(
            text="reMarkable 1",
            image_source=rm1_image,
            callback=lambda x: self.select_tablet("reMarkable 1")
        )
        self.devices_layout.add_widget(self.rm1)
        
        # reMarkable 2 button with image
        self.rm2 = DeviceButton(
            text="reMarkable 2",
            image_source=rm2_image,
            callback=lambda x: self.select_tablet("reMarkable 2")
        )
        self.devices_layout.add_widget(self.rm2)
        
        # reMarkable Paper Pro button with image
        self.rm_pro = DeviceButton(
            text="Paper Pro",
            image_source=rmpro_image,
            callback=lambda x: self.select_tablet("Paper Pro")
        )
        self.devices_layout.add_widget(self.rm_pro)
        
        self.layout.add_widget(self.devices_layout)
        
        # Information
        self.info = SafeLabel(
            text="Note: PDF templates are optimized for each specific device model",
            font_size=dp(14),
            italic=True,
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        self.layout.add_widget(self.info)
        
        # Color support info
        self.color_info = SafeLabel(
            text="Color support available for Paper Pro only",
            font_size=dp(14),
            italic=True,
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        self.layout.add_widget(self.color_info)
        
        # Add more spacing at bottom
        self.layout.add_widget(BoxLayout(size_hint_y=0.2))
        
        self.add_widget(self.layout)
        
        # Schedule a delayed layout update
        Clock.schedule_once(self.update_layout, 0.5)
    
    def update_layout(self, dt=None):
        """Update layout when the size changes."""
        if hasattr(self, 'layout'):
            self.layout.size = self.size
    
    def select_tablet(self, tablet_model):
        """Set the selected tablet model and move to the PDF preview screen."""
        app = App.get_running_app()
        # Use a safer approach with a try-except block
        try:
            app.select_tablet(tablet_model)
        except Exception as e:
            print(f"Error in select_tablet: {e}")
            # Try again after a delay
            Clock.schedule_once(lambda dt: app.select_tablet(tablet_model), 0.5)
