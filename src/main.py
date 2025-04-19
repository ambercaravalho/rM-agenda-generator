"""
Entry point for the reMarkable Agenda Generator application.
A simplified calendar PDF generator for reMarkable tablets.
"""
import os
import sys
from kivy.config import Config

# Configure Kivy before other imports
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')
Config.set('graphics', 'resizable', '1')

# Import Kivy dependencies
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.app import MDApp
from datetime import datetime
import tempfile
from utils.config_manager import ConfigManager
from views.settings_view import SettingsView
from utils.icon_helper import get_icon_button
from utils.setup_helper import safe_navigate

class TabletSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(TabletSelectionScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Header with title and settings button
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        title = Label(text="Select Your Device", font_size=dp(24), size_hint_x=1)
        
        # Settings button
        settings_button = get_icon_button(
            'cog',
            callback=self.open_settings,
            tooltip="Settings",
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        
        header.add_widget(title)
        header.add_widget(settings_button)
        
        # Tablet options
        tablets_layout = BoxLayout(spacing=dp(20))
        
        # reMarkable 1 button
        rm1_button = Button(text="reMarkable 1", size_hint_y=None, height=dp(100))
        rm1_button.bind(on_press=lambda x: app.select_tablet("reMarkable 1"))
        
        # reMarkable 2 button
        rm2_button = Button(text="reMarkable 2", size_hint_y=None, height=dp(100))
        rm2_button.bind(on_press=lambda x: app.select_tablet("reMarkable 2"))
        
        # PaperPro button
        rmpro_button = Button(text="Paper Pro", size_hint_y=None, height=dp(100))
        rmpro_button.bind(on_press=lambda x: app.select_tablet("Paper Pro"))
        
        # Add buttons to layout
        tablets_layout.add_widget(rm1_button)
        tablets_layout.add_widget(rm2_button)
        tablets_layout.add_widget(rmpro_button)
        
        # Add widgets to main layout
        layout.add_widget(header)
        layout.add_widget(Label(text="Please select your reMarkable tablet model:"))
        layout.add_widget(tablets_layout)
        
        self.add_widget(layout)
    
    def open_settings(self, instance):
        """Navigate to settings screen."""
        safe_navigate('settings', transition_direction='left')

class PDFPreviewScreen(Screen):
    def __init__(self, **kwargs):
        super(PDFPreviewScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Header with device info and settings button
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.device_label = Label(text="Selected Tablet: None", size_hint_x=1)
        
        # Settings button
        settings_button = get_icon_button(
            'cog',
            callback=self.open_settings,
            tooltip="Settings",
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        
        header.add_widget(self.device_label)
        header.add_widget(settings_button)
        
        # View type selection
        view_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        month_button = Button(text="Month View")
        month_button.bind(on_press=lambda x: self.change_view('month'))
        
        week_button = Button(text="Week View")
        week_button.bind(on_press=lambda x: self.change_view('week'))
        
        day_button = Button(text="Day View")
        day_button.bind(on_press=lambda x: self.change_view('day'))
        
        view_layout.add_widget(month_button)
        view_layout.add_widget(week_button)
        view_layout.add_widget(day_button)
        
        # Preview area with image
        self.preview_area = BoxLayout()
        self.preview_image = Image(allow_stretch=True, keep_ratio=True)
        self.preview_label = Label(text="Loading preview...")
        
        self.preview_area.add_widget(self.preview_image)
        
        # Generate button
        generate_layout = BoxLayout(size_hint_y=None, height=dp(50))
        generate_button = Button(text="Generate PDF")
        generate_button.bind(on_press=self.generate_pdf)
        generate_layout.add_widget(generate_button)
        
        # Add all widgets to main layout
        self.layout.add_widget(header)
        self.layout.add_widget(view_layout)
        self.layout.add_widget(self.preview_area)
        self.layout.add_widget(generate_layout)
        
        self.add_widget(self.layout)
        
        # Current view settings
        self.current_view = 'month'
        self.current_date = datetime.now()
        self.current_preview_path = None
    
    def open_settings(self, instance):
        """Navigate to settings screen."""
        safe_navigate('settings', transition_direction='left')
    
    def setup_preview(self, view_type, date):
        """Set up the preview with specified view type and date."""
        self.current_view = view_type
        self.current_date = date
        self.update_preview()
    
    def change_view(self, view_type):
        """Change the calendar view type."""
        self.current_view = view_type
        self.update_preview()
    
    def update_preview(self):
        """Update the preview based on current settings."""
        try:
            # Clear the previous preview if it exists
            if hasattr(self, 'preview_image'):
                self.preview_image.source = ''
            
            # Remove any existing temporary preview file
            if self.current_preview_path and os.path.exists(self.current_preview_path):
                try:
                    os.unlink(self.current_preview_path)
                except:
                    pass
            
            # Generate a new preview
            from utils.pdf_generator import generate_preview_image
            
            # Show loading indicator
            if hasattr(self, 'preview_label'):
                self.preview_area.clear_widgets()
                self.preview_area.add_widget(self.preview_label)
                self.preview_label.text = "Generating preview..."
            
            # Generate the preview image in a separate thread to avoid blocking UI
            def generate_preview_thread():
                try:
                    preview_path = generate_preview_image(self.current_view, self.current_date)
                    
                    if preview_path and os.path.exists(preview_path):
                        self.current_preview_path = preview_path
                        
                        # Update UI on the main thread
                        def update_ui_with_preview(dt):
                            self.preview_area.clear_widgets()
                            self.preview_image.source = preview_path
                            self.preview_area.add_widget(self.preview_image)
                        
                        Clock.schedule_once(update_ui_with_preview, 0)
                    else:
                        # Update UI on the main thread if preview generation failed
                        def show_error(dt):
                            self.preview_label.text = "Failed to generate preview"
                        
                        Clock.schedule_once(show_error, 0)
                        
                except Exception as e:
                    # Update UI on the main thread if there was an exception
                    def show_exception(dt):
                        self.preview_label.text = f"Error generating preview: {str(e)}"
                    
                    Clock.schedule_once(show_exception, 0)
            
            # Start the preview generation in a separate thread
            import threading
            preview_thread = threading.Thread(target=generate_preview_thread)
            preview_thread.daemon = True
            preview_thread.start()
            
        except Exception as e:
            if hasattr(self, 'preview_label'):
                self.preview_label.text = f"Error: {str(e)}"
    
    def generate_pdf(self, instance):
        """Generate the PDF file."""
        from utils.pdf_generator import generate_calendar_pdf
        
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate the PDF
            output_path = os.path.join(output_dir, f"calendar_{self.current_date.strftime('%Y-%m-%d')}.pdf")
            
            # Get the current app for device information
            supports_color = app.supports_color
            dimensions = app.dimensions
            
            # Generate PDF
            generate_calendar_pdf(self.current_view, self.current_date, output_path)
            
            # Show success message with popup
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            
            content = BoxLayout(orientation='vertical', padding=dp(10))
            content.add_widget(Label(text=f"PDF generated successfully!\nSaved to:\n{output_path}"))
            
            # Add button to open the output folder
            def open_folder(instance):
                import subprocess
                import platform
                
                try:
                    if platform.system() == "Windows":
                        os.startfile(os.path.dirname(output_path))
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", os.path.dirname(output_path)])
                    else:  # Linux
                        subprocess.call(["xdg-open", os.path.dirname(output_path)])
                except Exception as e:
                    print(f"Error opening folder: {e}")
                
                popup.dismiss()
            
            button = Button(text="Open Folder", size_hint_y=None, height=dp(50))
            button.bind(on_press=open_folder)
            content.add_widget(button)
            
            popup = Popup(title="PDF Generated", content=content, size_hint=(0.8, 0.4))
            popup.open()
            
        except Exception as e:
            # Show error message with popup
            from kivy.uix.popup import Popup
            
            popup = Popup(title="Error", content=Label(text=f"Error generating PDF:\n{str(e)}"), 
                          size_hint=(0.8, 0.4))
            popup.open()

class RemarkableAgendaApp(MDApp):
    def __init__(self, **kwargs):
        super(RemarkableAgendaApp, self).__init__(**kwargs)
        self.title = 'reMarkable Agenda Generator'
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Load device settings
        self.selected_tablet = self.config_manager.get_setting("device", "type")
        self.device_name = self.config_manager.get_setting("device", "name")
        self.supports_color = (self.selected_tablet == "Paper Pro")
        self.dimensions = self.get_dimensions(self.selected_tablet)
        
        # Display settings
        self.use_24h_time = self.config_manager.get_setting("display", "use_24h_time") == "True"
        self.monday_first = self.config_manager.get_setting("display", "monday_first") == "True"
        
        # Flag to track if setup is complete
        self.has_completed_setup = bool(self.selected_tablet)
    
    def build(self):
        # Create screen manager with slide transition for settings
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Create screens
        self.tablet_selection = TabletSelectionScreen(name='tablet_selection')
        self.pdf_preview = PDFPreviewScreen(name='pdf_preview')
        self.settings_view = SettingsView(name='settings')
        
        # Add screens to manager
        self.screen_manager.add_widget(self.tablet_selection)
        self.screen_manager.add_widget(self.pdf_preview)
        self.screen_manager.add_widget(self.settings_view)
        
        # Set initial screen
        if self.selected_tablet:
            self.pdf_preview.device_label.text = f"Selected Tablet: {self.selected_tablet}"
            self.pdf_preview.setup_preview('month', datetime.now())
            self.screen_manager.current = 'pdf_preview'
        else:
            self.screen_manager.current = 'tablet_selection'
        
        return self.screen_manager
    
    def on_settings_changed(self):
        """Handle settings changes from the settings screen."""
        # Reload all settings
        self.selected_tablet = self.config_manager.get_setting("device", "type")
        self.device_name = self.config_manager.get_setting("device", "name")
        self.supports_color = (self.selected_tablet == "Paper Pro")
        self.dimensions = self.get_dimensions(self.selected_tablet)
        
        # Update display settings
        self.use_24h_time = self.config_manager.get_setting("display", "use_24h_time") == "True"
        self.monday_first = self.config_manager.get_setting("display", "monday_first") == "True"
        
        # Update the PDF preview
        if hasattr(self, 'pdf_preview'):
            self.pdf_preview.device_label.text = f"Selected Tablet: {self.selected_tablet}"
            self.pdf_preview.update_preview()
    
    def select_tablet(self, tablet_model):
        """Set the selected tablet model and move to the PDF preview screen."""
        self.selected_tablet = tablet_model
        self.supports_color = (tablet_model == "Paper Pro")
        
        # Save to config manager
        self.config_manager.set_device_settings(
            self.device_name or "My reMarkable", 
            tablet_model
        )
        
        # Set completed setup flag
        self.has_completed_setup = True
        
        # Update PDF preview screen
        self.pdf_preview.device_label.text = f"Selected Tablet: {self.selected_tablet}"
        self.pdf_preview.setup_preview('month', datetime.now())
        
        # Navigate to PDF preview
        self.screen_manager.current = 'pdf_preview'
    
    def get_dimensions(self, tablet_model=None):
        """Get device dimensions based on the tablet model."""
        model = tablet_model or self.selected_tablet
        # All models currently have same dimensions
        return (1404, 1872)  # A5 size
    
    def format_time(self, time_obj):
        """Format a time object according to user's settings."""
        if self.use_24h_time:
            return time_obj.strftime("%H:%M")
        else:
            return time_obj.strftime("%I:%M %p")
    
    def get_week_start_day(self):
        """Get the week start day as an integer (0=Monday, 6=Sunday)."""
        return 0 if self.monday_first else 6

if __name__ == "__main__":
    # Set up necessary directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create directories if they don't exist
    for directory_name in ["config", "output", "assets"]:
        directory_path = os.path.join(current_dir, directory_name)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    
    # Create and start the application
    app = RemarkableAgendaApp()
    app.run()