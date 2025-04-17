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

from utils.pdf_generator import generate_calendar_pdf
from utils.ui_helpers import SafeLabel

class PDFPreviewView(Screen):
    """PDF preview and generation screen."""
    
    def __init__(self, **kwargs):
        super(PDFPreviewView, self).__init__(**kwargs)
        self.view_type = 'month'  # Default view type
        self.current_date = datetime.now()
        self.pdf_path = None
        
        # Calendar component options
        self.include_months = True
        self.include_weeks = True
        self.include_days = True
        
        # Define UI elements that need to be accessed before _init_ui
        self.layout = None
        self.left_panel = None
        self.center_panel = None
        self.right_panel = None
        self.device_label = None
        self.color_status = None
        self.view_type_btn = None
        self.date_label = None
        self.preview_image = None
        self.month_toggle = None
        self.week_toggle = None
        self.day_toggle = None
        self.view_type_dropdown = None
        
        # Create UI with delayed initialization to prevent layout errors
        Clock.schedule_once(self._init_ui, 0)
    
    def _init_ui(self, dt):
        """Initialize the UI with a delay to prevent layout errors."""
        # Main layout - horizontal with 3 sections
        self.layout = BoxLayout(orientation='horizontal', padding=dp(10), spacing=dp(10))
        
        # Left panel for options
        self.left_panel = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=dp(10), padding=dp(5))
        
        # Top bar with device info and back button
        self.top_bar = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(10))
        
        # Device info and back button in horizontal layout
        self.device_info_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # Use SafeLabel instead of regular Label
        self.device_label = SafeLabel(
            text="Selected Tablet: Not selected",
            size_hint_x=0.7
        )
        
        self.back_button = Button(
            text="Change Tablet",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(40)
        )
        self.back_button.bind(on_press=self.go_back_to_tablet_selection)
        
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
        
        # Add left panel to main layout
        self.layout.add_widget(self.left_panel)
        
        # Center panel for preview
        self.center_panel = BoxLayout(orientation='vertical', size_hint_x=0.5, padding=dp(5))
        
        # Preview title
        self.preview_title = SafeLabel(
            text="PDF Preview",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(18),
            bold=True,
            halign='center'
        )
        self.center_panel.add_widget(self.preview_title)
        
        # Preview image - use a BoxLayout to better constrain the image
        self.preview_container = BoxLayout(padding=dp(5))
        self.preview_image = Image(source='', allow_stretch=True, keep_ratio=True)
        self.preview_container.add_widget(self.preview_image)
        self.center_panel.add_widget(self.preview_container)
        
        # Add center panel to main layout
        self.layout.add_widget(self.center_panel)
        
        # Right panel for export options
        self.right_panel = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=dp(10), padding=dp(5))
        
        # Export options title
        self.export_title = SafeLabel(
            text="Export Options",
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            bold=True,
            halign='center'
        )
        self.right_panel.add_widget(self.export_title)
        
        # Save PDF button
        self.save_button = Button(
            text="Save PDF",
            size_hint_y=None,
            height=dp(50)
        )
        self.save_button.bind(on_press=self._safe_save_pdf)
        self.right_panel.add_widget(self.save_button)
        
        # Add some spacing
        self.right_panel.add_widget(Label())
        
        # Add right panel to main layout
        self.layout.add_widget(self.right_panel)
        
        # Add the main layout to the screen
        self.add_widget(self.layout)
        
        # Initialize view type dropdown
        self._init_dropdown()
    
    def _add_date_navigation(self):
        """Add date navigation controls to the left panel."""
        self.date_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.prev_btn = Button(text="<", size_hint_x=0.2)
        self.prev_btn.bind(on_press=lambda x: Clock.schedule_once(lambda dt: self.previous_date(), 0.1))
        
        # Use SafeLabel for date label
        self.date_label = SafeLabel(
            text=self.current_date.strftime("%B %Y"),
            size_hint_x=0.6,
            halign='center'
        )
        
        self.next_btn = Button(text=">", size_hint_x=0.2)
        self.next_btn.bind(on_press=lambda x: Clock.schedule_once(lambda dt: self.next_date(), 0.1))
        
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
            self.generate_preview()
        except Exception as e:
            print(f"Error selecting view type: {e}")
    
    def _safe_month_toggle(self, instance, value):
        """Safely handle month toggle."""
        try:
            self.include_months = (value == 'down')
            self.month_toggle.text = "Yes" if self.include_months else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling month view: {e}")
    
    def _safe_week_toggle(self, instance, value):
        """Safely handle week toggle."""
        try:
            self.include_weeks = (value == 'down')
            self.week_toggle.text = "Yes" if self.include_weeks else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling week view: {e}")
    
    def _safe_day_toggle(self, instance, value):
        """Safely handle day toggle."""
        try:
            self.include_days = (value == 'down')
            self.day_toggle.text = "Yes" if self.include_days else "No"
            Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
        except Exception as e:
            print(f"Error toggling day view: {e}")
    
    def _safe_save_pdf(self, *args):
        """Safely save the PDF."""
        Clock.schedule_once(lambda dt: self.save_pdf(), 0.1)
    
    def update_layout(self, dt=None):
        """Update the layout when the screen size changes."""
        if hasattr(self, 'layout') and self.layout:
            self.layout.size = self.size
    
    def update_date_label(self):
        """Update the date label based on view type and current date."""
        try:
            if not hasattr(self, 'date_label') or not self.date_label:
                print("Date label not initialized yet")
                return
                
            if self.view_type == 'month':
                self.date_label.text = self.current_date.strftime("%B %Y")
            elif self.view_type == 'week':
                # Calculate start and end of week
                start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                self.date_label.text = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
            elif self.view_type == 'day':
                self.date_label.text = self.current_date.strftime("%a, %b %d, %Y")
        except Exception as e:
            print(f"Error updating date label: {e}")
    
    def update_view_type_button(self):
        """Update the view type button text."""
        try:
            if not hasattr(self, 'view_type_btn') or not self.view_type_btn:
                print("View type button not initialized yet")
                return
                
            view_type_texts = {
                'month': 'Monthly Calendar',
                'week': 'Weekly Calendar',
                'day': 'Daily Calendar'
            }
            self.view_type_btn.text = f"Template: {view_type_texts.get(self.view_type, 'Monthly Calendar')}"
        except Exception as e:
            print(f"Error updating view type button: {e}")
    
    def previous_date(self):
        """Go to previous date based on view type."""
        try:
            if self.view_type == 'month':
                # Go to previous month
                if self.current_date.month == 1:
                    self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12, day=1)
                else:
                    self.current_date = self.current_date.replace(month=self.current_date.month - 1, day=1)
            elif self.view_type == 'week':
                # Go to previous week
                self.current_date -= timedelta(days=7)
            elif self.view_type == 'day':
                # Go to previous day
                self.current_date -= timedelta(days=1)
            
            self.update_date_label()
            self.generate_preview()
        except Exception as e:
            print(f"Error navigating to previous date: {e}")
    
    def next_date(self):
        """Go to next date based on view type."""
        try:
            if self.view_type == 'month':
                # Go to next month
                if self.current_date.month == 12:
                    self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1, day=1)
                else:
                    # Need to handle month length correctly
                    year = self.current_date.year
                    month = self.current_date.month + 1
                    if month > 12:
                        month = 1
                        year += 1
                    self.current_date = self.current_date.replace(year=year, month=month, day=1)
            elif self.view_type == 'week':
                # Go to next week
                self.current_date += timedelta(days=7)
            elif self.view_type == 'day':
                # Go to next day
                self.current_date += timedelta(days=1)
            
            self.update_date_label()
            self.generate_preview()
        except Exception as e:
            print(f"Error navigating to next date: {e}")
    
    def generate_preview(self):
        """Generate a PDF preview based on current settings."""
        try:
            # Create a temp directory if it doesn't exist
            temp_dir = os.path.join("assets", "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Generate a temporary PDF file
            temp_pdf = os.path.join(temp_dir, "preview.pdf")
            
            # Check if we have all the necessary components initialized
            if not hasattr(self, 'preview_image') or not self.preview_image:
                print("Preview image not initialized yet")
                return
                
            # Generate the PDF with component options
            self.pdf_path = generate_calendar_pdf(
                self.view_type, 
                self.current_date, 
                temp_pdf,
                include_months=self.include_months,
                include_weeks=self.include_weeks,
                include_days=self.include_days
            )
            
            # For a real application, you would convert PDF to image for preview
            # Here we're using a placeholder approach
            placeholder_image = os.path.join("assets", "images", "preview_placeholder.png")
            if os.path.exists(placeholder_image):
                self.preview_image.source = placeholder_image
                self.preview_image.reload()
            else:
                print(f"Preview placeholder image not found: {placeholder_image}")
        except Exception as e:
            print(f"Error generating PDF preview: {e}")
    
    def save_pdf(self):
        """Save the generated PDF file."""
        try:
            if not self.pdf_path or not os.path.exists(self.pdf_path):
                print("No PDF file to save")
                return
            
            # Use plyer's filechooser to get save location
            save_path = filechooser.save_file(title="Save Calendar PDF", 
                                              filters=[("PDF Files", "*.pdf")])
            
            if save_path and len(save_path) > 0:
                save_path = save_path[0]
                # Generate a fresh PDF at the selected location with component options
                generate_calendar_pdf(
                    self.view_type, 
                    self.current_date, 
                    save_path,
                    include_months=self.include_months,
                    include_weeks=self.include_weeks,
                    include_days=self.include_days
                )
                
                # Show confirmation
                popup = Popup(title='PDF Saved',
                              content=Label(text=f'Calendar saved to:\n{save_path}'),
                              size_hint=(None, None), size=(dp(400), dp(200)))
                popup.open()
                # Auto-dismiss after 3 seconds
                Clock.schedule_once(popup.dismiss, 3)
        except Exception as e:
            # Show error
            print(f"Error saving PDF: {e}")
            popup = Popup(title='Error',
                          content=Label(text=f'Failed to save PDF:\n{str(e)}'),
                          size_hint=(None, None), size=(dp(400), dp(200)))
            popup.open()
            Clock.schedule_once(popup.dismiss, 3)

    def setup_preview(self, view_type, date):
        """Set up the PDF preview based on view type and date. This is the main entry point."""
        try:
            # Store the parameters even if UI isn't ready yet
            self.view_type = view_type
            self.current_date = date
            
            # If UI isn't initialized yet, schedule this call for later
            if not hasattr(self, 'layout') or not self.layout:
                print("UI not initialized yet, scheduling setup for later")
                Clock.schedule_once(lambda dt: self.setup_preview(view_type, date), 0.5)
                return
            
            # Update UI elements with a bit of delay to ensure they're ready
            def delayed_setup(dt):
                try:
                    self.update_date_label()
                    self.update_view_type_button()
                    self.generate_preview()
                    
                    # Update color status based on selected device
                    app = App.get_running_app()
                    if hasattr(self, 'color_status') and self.color_status:
                        self.color_status.text = f"Color support: {'Enabled' if app.supports_color else 'Disabled'}"
                    
                    # Update device label
                    if hasattr(self, 'device_label') and self.device_label:
                        self.device_label.text = f"Selected Tablet: {app.selected_tablet or 'Not selected'}"
                except Exception as e:
                    print(f"Error in delayed setup: {e}")
            
            # Schedule the delayed setup
            Clock.schedule_once(delayed_setup, 0.2)
            
        except Exception as e:
            print(f"Error setting up preview: {e}")
    
    def go_back_to_tablet_selection(self, *args):
        """Go back to the tablet selection screen."""
        try:
            app = App.get_running_app()
            # Use a delayed transition to avoid mid-update issues
            Clock.schedule_once(lambda dt: setattr(app.screen_manager, 'current', 'tablet_selection'), 0.1)
        except Exception as e:
            print(f"Error going back to tablet selection: {e}")
