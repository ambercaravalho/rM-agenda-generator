"""
Main application class for the reMarkable Agenda Generator.
"""
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

from views.calendar_view import CalendarView
from views.settings_view import SettingsView
from views.pdf_preview_view import PDFPreviewView

class MainWindow(Screen):
    """Main window container for the application."""
    pass

class RemarkableAgendaApp(App):
    """Main application class for the reMarkable Agenda Generator."""
    
    def build(self):
        """Build and return the root widget for the application."""
        self.title = "reMarkable Agenda Generator"
        
        # Create the screen manager
        self.sm = ScreenManager()
        
        # Add the main screen
        main_screen = MainWindow(name='main')
        self.sm.add_widget(main_screen)
        
        # Add the settings screen
        settings_screen = SettingsView(name='settings')
        self.sm.add_widget(settings_screen)
        
        # Add the PDF preview screen
        pdf_preview_screen = PDFPreviewView(name='pdf_preview')
        self.sm.add_widget(pdf_preview_screen)
        
        return self.sm
    
    def get_application_config(self):
        """Return the path to the configuration file."""
        return super(RemarkableAgendaApp, self).get_application_config(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'remarkable_agenda.ini'))