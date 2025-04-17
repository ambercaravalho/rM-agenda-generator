"""
Main application module for reMarkable Agenda Generator.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.clock import Clock
import os

# Import views
from views.tablet_selection_view import TabletSelectionView
from views.calendar_view import CalendarView
from views.pdf_preview_view import PDFPreviewView
from views.settings_view import SettingsView

# Set application properties
Config.set('kivy', 'window_icon', 'assets/icon.png')
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Add the assets directory to the resource path
resource_add_path(os.path.join(os.path.dirname(__file__), 'assets'))

class MainScreen(Screen):
    """Main screen with navigation options."""
    pass

class RemarkableAgendaApp(App):
    """Main application class for the reMarkable Agenda Generator."""
    
    def build(self):
        """Build the application UI."""
        # Set default window size
        Window.size = (1200, 800)
        
        # Initialize app state
        self.tablet_model = None
        self.current_date = None
        self.view_type = 'month'
        self.events = {}
        self.weather = {}
        self.tasks = []
        
        # Initialize screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Add the tablet selection screen
        tablet_screen = TabletSelectionView(name='tablet_selection')
        self.screen_manager.add_widget(tablet_screen)
        
        # Add the calendar view screen
        calendar_screen = CalendarView(name='calendar')
        self.screen_manager.add_widget(calendar_screen)
        
        # Add the PDF preview screen
        pdf_preview_screen = PDFPreviewView(name='pdf_preview')
        self.screen_manager.add_widget(pdf_preview_screen)
        
        # Set the tablet selection as the default screen
        self.screen_manager.current = 'tablet_selection'
        
        return self.screen_manager
    
    def set_tablet_model(self, model):
        """Set the selected tablet model and move to calendar view."""
        self.tablet_model = model
        self.screen_manager.current = 'calendar'
    
    def show_pdf_preview(self, view_type, date):
        """Show the PDF preview with the current settings."""
        self.view_type = view_type
        self.current_date = date
        
        # Update the PDF preview screen with current data
        pdf_screen = self.screen_manager.get_screen('pdf_preview')
        pdf_screen.set_view_data(view_type, date, self.tablet_model, self.events, self.weather, self.tasks)
        self.screen_manager.current = 'pdf_preview'