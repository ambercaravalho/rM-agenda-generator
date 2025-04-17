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
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime

class TabletSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(TabletSelectionScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        title = Label(text="Select Your Device", font_size=dp(24), size_hint_y=None, height=dp(50))
        
        # Tablet options
        tablets_layout = BoxLayout(spacing=dp(20))
        
        # reMarkable 1 button
        rm1_button = Button(text="reMarkable 1", size_hint_y=None, height=dp(100))
        rm1_button.bind(on_press=lambda x: app.select_tablet("reMarkable 1"))
        
        # reMarkable 2 button
        rm2_button = Button(text="reMarkable 2", size_hint_y=None, height=dp(100))
        rm2_button.bind(on_press=lambda x: app.select_tablet("reMarkable 2"))
        
        # Add buttons to layout
        tablets_layout.add_widget(rm1_button)
        tablets_layout.add_widget(rm2_button)
        
        # Add widgets to main layout
        layout.add_widget(title)
        layout.add_widget(Label(text="Please select your reMarkable tablet model:"))
        layout.add_widget(tablets_layout)
        
        self.add_widget(layout)

class PDFPreviewScreen(Screen):
    def __init__(self, **kwargs):
        super(PDFPreviewScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Header with device info
        header = BoxLayout(size_hint_y=None, height=dp(50))
        self.device_label = Label(text="Selected Tablet: None")
        header.add_widget(self.device_label)
        
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
        
        # Preview area (placeholder)
        self.preview_area = BoxLayout()
        self.preview_label = Label(text="Calendar preview will appear here")
        self.preview_area.add_widget(self.preview_label)
        
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
        self.preview_label.text = f"{self.current_view.capitalize()} View\n{self.current_date.strftime('%B %Y')}"
    
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
            
            # Show success message
            self.preview_label.text = f"PDF generated successfully!\nSaved to: {output_path}"
            
        except Exception as e:
            self.preview_label.text = f"Error generating PDF: {str(e)}"

class RemarkableAgendaApp(App):
    def __init__(self, **kwargs):
        super(RemarkableAgendaApp, self).__init__(**kwargs)
        self.title = 'reMarkable Agenda Generator'
        self.selected_tablet = None
        self.supports_color = False
        self.dimensions = (1404, 1872)  # Default to A5 (reMarkable 2)
        
        # Load saved settings if they exist
        self.load_settings()
    
    def build(self):
        # Create screen manager for navigation
        self.screen_manager = ScreenManager(transition=NoTransition())
        
        # Create screens
        self.tablet_selection = TabletSelectionScreen(name='tablet_selection')
        self.pdf_preview = PDFPreviewScreen(name='pdf_preview')
        
        # Add screens to manager
        self.screen_manager.add_widget(self.tablet_selection)
        self.screen_manager.add_widget(self.pdf_preview)
        
        # Set initial screen
        if self.selected_tablet:
            self.pdf_preview.device_label.text = f"Selected Tablet: {self.selected_tablet}"
            self.pdf_preview.setup_preview('month', datetime.now())
            self.screen_manager.current = 'pdf_preview'
        else:
            self.screen_manager.current = 'tablet_selection'
        
        return self.screen_manager
    
    def select_tablet(self, tablet_model):
        """Set the selected tablet model and move to the PDF preview screen."""
        self.selected_tablet = tablet_model
        self.supports_color = (tablet_model == "Paper Pro")
        self.save_settings()
        
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
    
    def load_settings(self):
        """Load settings from a simple JSON file."""
        import json
        
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        config_file = os.path.join(config_dir, "simple_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    self.selected_tablet = settings.get('tablet_model')
            except:
                # If there's an error, just use defaults
                pass
    
    def save_settings(self):
        """Save settings to a simple JSON file."""
        import json
        
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        config_file = os.path.join(config_dir, "simple_config.json")
        settings = {
            'tablet_model': self.selected_tablet
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Could not save settings: {e}")

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