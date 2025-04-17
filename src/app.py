"""
Main application class for the reMarkable Agenda Generator.
Implements a three-step workflow: tablet selection, PDF preview, and generation.
"""
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition, FadeTransition
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock

from views.tablet_selection_view import TabletSelectionView
from views.pdf_preview_view import PDFPreviewView

# Set of pre-loaded screens to prevent recreation issues
PRELOADED_SCREENS = {}

class RemarkableAgendaApp(App):
    """reMarkable Agenda Generator application."""
    
    def __init__(self, **kwargs):
        super(RemarkableAgendaApp, self).__init__(**kwargs)
        self.title = "reMarkable Agenda Generator"
        self.selected_tablet = None
        self.supports_color = False
        self.dimensions = self.get_dimensions("reMarkable 2")  # Default dimensions
        
        # Important: Create screen manager with a safe transition
        self.screen_manager = ScreenManager(transition=NoTransition())
        
        # Flag to track if the app has been built
        self.is_built = False
        
        # Store last error to prevent cascading errors
        self.last_error_time = 0
        self.error_count = 0

    def build(self):
        """Build the application UI."""
        # Preload all screens to prevent recreation issues
        self._preload_screens()
        
        # Set up the app as built
        self.is_built = True
        
        # Add a delayed layout update to ensure everything is properly sized
        Clock.schedule_once(self.update_layouts, 0.5)
        
        return self.screen_manager
        
    def _preload_screens(self):
        """Preload all screens to prevent recreation issues during transitions."""
        global PRELOADED_SCREENS
        
        # Create each screen only once
        if 'tablet_selection' not in PRELOADED_SCREENS:
            PRELOADED_SCREENS['tablet_selection'] = TabletSelectionView(name="tablet_selection")
            
        if 'pdf_preview' not in PRELOADED_SCREENS:
            PRELOADED_SCREENS['pdf_preview'] = PDFPreviewView(name="pdf_preview")
            
        # Add preloaded screens to the screen manager
        for screen_name, screen in PRELOADED_SCREENS.items():
            if screen.name not in [s.name for s in self.screen_manager.screens]:
                self.screen_manager.add_widget(screen)
                
        # Start with tablet selection
        self.screen_manager.current = "tablet_selection"
        
    def update_layouts(self, dt=None):
        """
        Update all screen layouts safely to handle window resizing.
        This is called on resize events to ensure layouts adjust properly.
        """
        try:
            # Only proceed if the app is fully built
            if not self.is_built:
                return
                
            # Request layout updates for all screens
            for screen in self.screen_manager.screens:
                # Force a layout update on the screen
                if hasattr(screen, 'update_layout'):
                    screen.update_layout()
                else:
                    # Generic approach - trigger size update
                    screen.size = screen.size
                    if hasattr(screen, 'layout'):
                        screen.layout.size = screen.layout.size
                        
        except Exception as e:
            print(f"Layout update error (non-fatal): {e}")
    
    def select_tablet(self, tablet_model):
        """
        Set the selected tablet model and move to the PDF preview screen.
        
        Args:
            tablet_model: The selected tablet model string
        """
        try:
            # Set selected tablet
            self.selected_tablet = tablet_model
            
            # Set color support based on device
            self.supports_color = (tablet_model == "Paper Pro")
            
            # Update dimensions
            self.dimensions = self.get_dimensions(tablet_model)
            
            # Schedule transition to avoid immediate change issues
            Clock.schedule_once(lambda dt: self._safe_transition_to_preview(), 0.1)
            
        except Exception as e:
            print(f"Error selecting tablet: {e}")
    
    def _safe_transition_to_preview(self):
        """Safely transition to the PDF preview screen."""
        try:
            # Get the screen and prepare it
            preview_screen = PRELOADED_SCREENS['pdf_preview']
            
            # Update tablet info on the preview screen
            if hasattr(preview_screen, 'device_label'):
                preview_screen.device_label.text = f"Selected Tablet: {self.selected_tablet}"
            
            # Setup the PDF preview with default settings
            preview_screen.setup_preview('month', datetime.now())
            
            # Use safe screen transition
            self.screen_manager.current = "pdf_preview"
            
        except Exception as e:
            print(f"Error transitioning to preview: {e}")
    
    def show_pdf_preview(self, view_type, date):
        """
        Show the PDF preview screen with the specified view type and date.
        
        Args:
            view_type: The type of calendar view ('month', 'week', or 'day')
            date: The date to generate the preview for
        """
        try:
            # Get the screen and prepare it
            preview_screen = PRELOADED_SCREENS['pdf_preview']
            
            # Update tablet info on the preview screen
            if hasattr(preview_screen, 'device_label'):
                preview_screen.device_label.text = f"Selected Tablet: {self.selected_tablet}"
            
            # Setup the PDF preview
            preview_screen.setup_preview(view_type, date)
            
            # Use safe screen transition
            self.screen_manager.current = "pdf_preview"
            
        except Exception as e:
            print(f"Error showing PDF preview: {e}")
    
    def get_dimensions(self, tablet_model=None):
        """
        Get the dimensions for the specified tablet model.
        
        Args:
            tablet_model: The tablet model to get dimensions for, or None for the current model
            
        Returns:
            A dictionary containing width_pt, height_pt, and dpi values
        """
        if tablet_model is None:
            tablet_model = self.selected_tablet or "reMarkable 2"
        
        # Dimensions in points (1/72 inch)
        if tablet_model == "reMarkable 1":
            return {
                'width_pt': 595,  # 8.27 inches * 72 pts/in
                'height_pt': 842,  # 11.69 inches * 72 pts/in
                'dpi': 226
            }
        elif tablet_model == "reMarkable 2":
            return {
                'width_pt': 595,  # 8.27 inches * 72 pts/in
                'height_pt': 842,  # 11.69 inches * 72 pts/in
                'dpi': 226
            }
        elif tablet_model == "Paper Pro":
            return {
                'width_pt': 612,  # 8.5 inches * 72 pts/in
                'height_pt': 792,  # 11 inches * 72 pts/in
                'dpi': 300
            }
        else:
            # Default to reMarkable 2
            return {
                'width_pt': 595,
                'height_pt': 842,
                'dpi': 226
            }