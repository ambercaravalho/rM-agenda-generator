"""
PDF preview and generation screen for the reMarkable Agenda Generator.
"""
import os
from datetime import datetime, timedelta
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
from plyer import filechooser
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput

from utils.pdf_generator import generate_calendar_pdf
from utils.ui_helpers import SafeLabel
from utils.icon_helper import get_icon_button
from utils.setup_helper import safe_navigate
from utils.theme_manager import ThemeManager

class PDFPreviewView(Screen):
    """PDF preview and generation screen."""
    
    def __init__(self, **kwargs):
        super(PDFPreviewView, self).__init__(**kwargs)
        self.view_type = 'month'
        self.current_date = datetime.now()
        self.pdf_path = None
        self.include_months = True
        self.include_weeks = True
        self.include_days = True
        
        # Initialize UI
        self.layout = BoxLayout(orientation='horizontal', padding=dp(10), spacing=dp(15))
        
        # Left panel for controls (1/3 of width)
        self.left_panel = BoxLayout(orientation='vertical', spacing=dp(15), 
                                    size_hint_x=0.3)
        
        # Right panel for preview (2/3 of width)
        self.right_panel = BoxLayout(orientation='vertical', spacing=dp(10),
                                    size_hint_x=0.7)
        
        # Add panels to main layout
        self.layout.add_widget(self.left_panel)
        self.layout.add_widget(self.right_panel)
        
        # Initialize the dropdown
        self._init_dropdown()
        
        # Add the layout to the screen with a delayed initialization
        self.add_widget(self.layout)
        Clock.schedule_once(self._init_ui, 0.1)
    
    def _init_ui(self, dt):
        """Initialize the UI with a delay to prevent layout errors."""
        try:
            # Clear existing widgets
            self.left_panel.clear_widgets()
            self.right_panel.clear_widgets()
            
            # Top controls for the left panel
            self.top_bar = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
            
            # Device info row
            self.device_info_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            self.device_label = SafeLabel(
                text="Selected Tablet: Unknown",
                size_hint_x=0.7,
                halign='left'
            )
            
            # Change tablet button with icon
            self.back_button = get_icon_button(
                'tablet', 
                callback=self.go_back_to_tablet_selection,
                tooltip="Change Tablet",
                size_hint_x=0.3,
                size_hint_y=None,
                height=dp(40)
            )
            
            self.device_info_row.add_widget(self.device_label)
            self.device_info_row.add_widget(self.back_button)
            self.top_bar.add_widget(self.device_info_row)
            
            # Color indicator
            self.color_status = SafeLabel(
                text="Color support: Unknown",
                italic=True,
                font_size=dp(14),
                size_hint_y=None,
                height=dp(30)
            )
            self.top_bar.add_widget(self.color_status)
            
            self.left_panel.add_widget(self.top_bar)
            
            # Add components options, date navigation, etc.
            self._add_date_navigation()
            self._add_view_selector()
            self._add_component_options()
            
            # Action buttons at the bottom
            self.action_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
            
            # Create PDF button with icon
            self.create_pdf_button = get_icon_button(
                'file-pdf-box', 
                callback=self.generate_pdf,
                tooltip="Generate PDF",
                text="Generate PDF",
                size_hint_x=0.7
            )
            
            # Settings button with icon
            self.settings_button = get_icon_button(
                'cog', 
                callback=self.open_settings,
                tooltip="Settings",
                size_hint_x=0.3
            )
            
            self.action_buttons.add_widget(self.create_pdf_button)
            self.action_buttons.add_widget(self.settings_button)
            self.left_panel.add_widget(self.action_buttons)
            
            # Preview area (right panel)
            self.preview_label = SafeLabel(
                text="PDF Preview",
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(30),
                halign='center'
            )
            self.right_panel.add_widget(self.preview_label)
            
            # Preview image
            self.preview_image = Image(
                source="assets/images/preview_placeholder.png",
                allow_stretch=True,
                keep_ratio=True
            )
            self.right_panel.add_widget(self.preview_image)
            
        except Exception as e:
            print(f"Error initializing UI: {e}")
    
    def _add_date_navigation(self):
        """Add date navigation controls to the left panel."""
        self.date_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Previous button with icon
        self.prev_btn = get_icon_button(
            'arrow-left', 
            callback=lambda x: Clock.schedule_once(lambda dt: self.previous_date(), 0.1),
            tooltip="Previous Month",
            size_hint_x=0.2
        )
        
        # Use SafeLabel for date label
        self.date_label = SafeLabel(
            text=self.current_date.strftime("%B %Y"),
            size_hint_x=0.6,
            halign='center'
        )
        
        # Next button with icon
        self.next_btn = get_icon_button(
            'arrow-right', 
            callback=lambda x: Clock.schedule_once(lambda dt: self.next_date(), 0.1),
            tooltip="Next Month",
            size_hint_x=0.2
        )
        
        self.date_nav.add_widget(self.prev_btn)
        self.date_nav.add_widget(self.date_label)
        self.date_nav.add_widget(self.next_btn)
        
        self.left_panel.add_widget(self.date_nav)
    
    def _add_view_selector(self):
        """Add view type selector to the left panel."""
        # View type selector
        self.view_type_btn = Button(
            text="Template: Monthly Calendar",
            size_hint_y=None,
            height=dp(50)
        )
        self.view_type_btn.bind(on_release=self._safe_show_dropdown)
        self.left_panel.add_widget(self.view_type_btn)
    
    def _add_component_options(self):
        """Add calendar component options to the left panel."""
        # Calendar component options section
        self.components_label = SafeLabel(
            text="Calendar Components:",
            size_hint_y=None,
            height=dp(40),
            bold=True,
            halign='center'
        )
        self.left_panel.add_widget(self.components_label)
        
        # Month option
        self.month_option_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.month_option_row.add_widget(SafeLabel(text="Include Monthly View", size_hint_x=0.7))
        
        self.month_toggle = ToggleButton(text="Yes", state="down", size_hint_x=0.3)
        self.month_toggle.bind(state=self._safe_month_toggle)
        self.month_option_row.add_widget(self.month_toggle)
        self.left_panel.add_widget(self.month_option_row)
        
        # Week option
        self.week_option_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.week_option_row.add_widget(SafeLabel(text="Include Weekly View", size_hint_x=0.7))
        
        self.week_toggle = ToggleButton(text="Yes", state="down", size_hint_x=0.3)
        self.week_toggle.bind(state=self._safe_week_toggle)
        self.week_option_row.add_widget(self.week_toggle)
        self.left_panel.add_widget(self.week_option_row)
        
        # Day option
        self.day_option_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.day_option_row.add_widget(SafeLabel(text="Include Daily View", size_hint_x=0.7))
        
        self.day_toggle = ToggleButton(text="Yes", state="down", size_hint_x=0.3)
        self.day_toggle.bind(state=self._safe_day_toggle)
        self.day_option_row.add_widget(self.day_toggle)
        self.left_panel.add_widget(self.day_option_row)
        
        # Add some spacing
        self.left_panel.add_widget(Label())
    
    def _init_dropdown(self):
        """Initialize view type dropdown."""
        self.view_type_dropdown = DropDown()
        view_types = [
            ('Monthly Calendar', 'month'),
            ('Weekly Calendar', 'week'),
            ('Daily Calendar', 'day')
        ]
        
        for name, view_type in view_types:
            btn = Button(text=name, size_hint_y=None, height=dp(44))
            btn.view_type = view_type
            # Use a partial function to safely bind the button
            btn.bind(on_release=partial(self._on_dropdown_select, view_type=view_type))
            self.view_type_dropdown.add_widget(btn)
    
    def _on_dropdown_select(self, instance, view_type):
        """Handle dropdown item selection with direct view_type parameter."""
        self.view_type_dropdown.dismiss()
        Clock.schedule_once(lambda dt: self._safe_view_type_select(view_type), 0.1)
    
    def update_view_type_button(self):
        """Update the view type button text based on the current selection."""
        view_type_names = {
            'month': 'Monthly Calendar',
            'week': 'Weekly Calendar',
            'day': 'Daily Calendar'
        }
        if hasattr(self, 'view_type_btn'):
            self.view_type_btn.text = f"Template: {view_type_names.get(self.view_type, 'Unknown')}"
    
    def go_back_to_tablet_selection(self, instance):
        """Return to the tablet selection screen."""
        safe_navigate('tablet_selection', transition_direction='right')
    
    def open_settings(self, instance):
        """Open the settings screen."""
        safe_navigate('settings', transition_direction='left')
    
    def previous_date(self):
        """Navigate to the previous month/week/day."""
        if self.view_type == 'month':
            # Go to previous month
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12, day=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month-1, day=1)
        elif self.view_type == 'week':
            # Go to previous week
            self.current_date -= timedelta(days=7)
        else:
            # Go to previous day
            self.current_date -= timedelta(days=1)
            
        self.update_date_display()
        self.generate_preview()
    
    def next_date(self):
        """Navigate to the next month/week/day."""
        if self.view_type == 'month':
            # Go to next month
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1, day=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month+1, day=1)
        elif self.view_type == 'week':
            # Go to next week
            self.current_date += timedelta(days=7)
        else:
            # Go to next day
            self.current_date += timedelta(days=1)
            
        self.update_date_display()
        self.generate_preview()
    
    def update_date_display(self):
        """Update the date label based on the current view type and date."""
        if self.view_type == 'month':
            self.date_label.text = self.current_date.strftime("%B %Y")
        elif self.view_type == 'week':
            # Calculate start and end of week
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.date_label.text = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
        else:
            self.date_label.text = self.current_date.strftime("%A, %b %d, %Y")
    
    def generate_preview(self):
        """Generate a preview of the PDF."""
        try:
            app = App.get_running_app()
            
            # Generate the PDF
            output_dir = os.path.join(os.getcwd(), "output")
            
            # Create components configuration based on toggle buttons
            components = {
                'month': self.include_months,
                'week': self.include_weeks,
                'day': self.include_days
            }
            
            dimensions = app.dimensions
            supports_color = app.supports_color
            
            # Call the PDF generator
            self.pdf_path = generate_calendar_pdf(
                self.view_type,
                self.current_date,
                output_dir,
                dimensions,
                components,
                supports_color
            )
            
            # Show a preview of the first page
            if self.pdf_path and os.path.exists(self.pdf_path):
                # TODO: Generate an image preview of the PDF
                # For now, just show a placeholder
                self.preview_image.source = "assets/images/preview_placeholder.png"
                self.preview_image.reload()
                
        except Exception as e:
            print(f"Error generating preview: {e}")
            # Show a placeholder
            self.preview_image.source = "assets/images/preview_placeholder.png"
            self.preview_image.reload()
    
    def generate_pdf(self, *args):
        """Generate and save the PDF."""
        try:
            # Show a loading indicator
            self._show_loading_popup("Generating PDF...")
            
            # Get app instance
            app = App.get_running_app()
            
            # Create a unique filename based on the current date and view type
            filename = f"remarkable_calendar_{self.view_type}_{self.current_date.strftime('%Y%m%d')}.pdf"
            output_path = os.path.join("output", filename)
            
            # Schedule the actual generation with a short delay to allow loading popup to appear
            Clock.schedule_once(lambda dt: self._perform_pdf_generation(output_path, app), 0.1)
        except Exception as e:
            print(f"Error initiating PDF generation: {e}")
            # Show error popup
            popup = Popup(
                title='Error',
                content=Label(text=f"Could not generate PDF: {str(e)}"),
                size_hint=(None, None),
                size=(dp(400), dp(200))
            )
            popup.open()
    
    def _perform_pdf_generation(self, output_path, app):
        """Perform the actual PDF generation in a separate function."""
        try:
            # Determine which components to include
            include = {
                'month': self.include_months,
                'week': self.include_weeks,
                'day': self.include_days
            }
            
            # Generate the PDF
            generate_calendar_pdf(
                output_path,
                self.current_date,
                supports_color=app.supports_color,
                include=include,
                dimensions=app.dimensions,
                view_type=self.view_type
            )
            
            # Dismiss loading popup
            if hasattr(self, '_loading_popup') and self._loading_popup:
                self._loading_popup.dismiss()
                self._loading_popup = None
            
            # Show success popup
            self.show_save_success(output_path)
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Dismiss loading popup
            if hasattr(self, '_loading_popup') and self._loading_popup:
                self._loading_popup.dismiss()
                self._loading_popup = None
                
            # Show error popup
            popup = Popup(
                title='Error',
                content=Label(text=f"Could not generate PDF: {str(e)}"),
                size_hint=(None, None),
                size=(dp(400), dp(200))
            )
            popup.open()
    
    def _show_loading_popup(self, message="Loading..."):
        """Show a loading popup."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        
        # Create and store the popup
        self._loading_popup = Popup(
            title='Please Wait',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(150)),
            auto_dismiss=False
        )
        self._loading_popup.open()
    
    def save_pdf(self, selected_path):
        """Save the generated PDF to the selected location."""
        if not selected_path or not self.pdf_path:
            return
            
        try:
            import shutil
            destination = selected_path[0]
            
            # Make sure it has .pdf extension
            if not destination.lower().endswith('.pdf'):
                destination += '.pdf'
                
            # Copy the file
            shutil.copy2(self.pdf_path, destination)
            
            # Show success message
            self.show_save_success(destination)
            
        except Exception as e:
            print(f"Error saving PDF: {e}")
            self.show_save_error()
    
    def show_save_success(self, path):
        """Show a success popup after saving PDF."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=f"PDF successfully saved to:"))
        content.add_widget(Label(text=f"{os.path.basename(path)}", bold=True))
        
        # Add an open file button if plyer can do it
        try:
            from plyer import utils
            if hasattr(utils, 'open_file'):
                open_button = get_icon_button(
                    'open-in-app',
                    callback=lambda x: utils.open_file(path),
                    text="Open PDF",
                    tooltip="Open the PDF file"
                )
                content.add_widget(open_button)
        except:
            pass
        
        popup = Popup(title='PDF Saved', content=content,
                     size_hint=(None, None), size=(dp(400), dp(200)))
        
        # Add close button
        close_button = get_icon_button('close', callback=popup.dismiss, tooltip="Close")
        content.add_widget(close_button)
        
        popup.open()
    
    def show_save_error(self):
        """Show an error popup if saving fails."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Error saving PDF file."))
        content.add_widget(Label(text="Please check permissions and try again."))
        
        popup = Popup(title='Error', content=content,
                     size_hint=(None, None), size=(dp(400), dp(200)))
        
        # We need to create the popup first, then add the button that refers to it
        close_button = Button(
            text="Close",
            size_hint_y=None,
            height=dp(40)
        )
        close_button.bind(on_press=popup.dismiss)
        content.add_widget(close_button)
        
        popup.open()
    
    def setup_preview(self, view_type, date):
        """Setup the preview with the given view type and date."""
        self.view_type = view_type
        self.current_date = date
        
        # Update device info
        app = App.get_running_app()
        if app.selected_tablet:
            self.device_label.text = f"Selected Tablet: {app.selected_tablet}"
            
        # Update color support indicator
        if app.supports_color:
            self.color_status.text = "Color support: Yes"
        else:
            self.color_status.text = "Color support: No"
        
        # Update view type button
        self.update_view_type_button()
        
        # Update date display
        self.update_date_display()
        
        # Generate preview
        self.generate_preview()
    
    def _safe_show_dropdown(self, button):
        """Safely show the dropdown menu."""
        try:
            self.view_type_dropdown.open(button)
        except Exception as e:
            print(f"Error showing dropdown: {e}")
    
    def _safe_view_type_select(self, view_type):
        """Safely handle view type selection."""
        try:
            self.view_type = view_type
            self.update_view_type_button()
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error selecting view type: {e}")
            # Try again with a delay
            Clock.schedule_once(lambda dt: self._retry_view_type_select(view_type), 0.5)
    
    def _retry_view_type_select(self, view_type):
        """Retry view type selection after a delay."""
        try:
            self.view_type = view_type
            self.update_view_type_button()
            self.generate_preview()
        except Exception as e:
            print(f"Retry view type selection also failed: {e}")
    
    def _safe_month_toggle(self, instance, value):
        """Safely handle month toggle."""
        try:
            self.include_months = (value == 'down')
            instance.text = "Yes" if self.include_months else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling month view: {e}")
    
    def _safe_week_toggle(self, instance, value):
        """Safely handle week toggle."""
        try:
            self.include_weeks = (value == 'down')
            instance.text = "Yes" if self.include_weeks else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling week view: {e}")
    
    def _safe_day_toggle(self, instance, value):
        """Safely handle day toggle."""
        try:
            self.include_days = (value == 'down')
            instance.text = "Yes" if self.include_days else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling day view: {e}")
    
    def update_layout(self, dt=None):
        """Update layout when the size changes."""
        # Make sure right panel fills available space
        if hasattr(self, 'layout') and hasattr(self, 'right_panel'):
            self.right_panel.size_hint_x = 0.7
