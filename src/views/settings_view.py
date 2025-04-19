"""
Settings view screen for the reMarkable Agenda Generator.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.graphics import Color, Rectangle
from functools import partial
from kivy.uix.popup import Popup
from kivy.clock import Clock
from utils.config_manager import ConfigManager
from utils.icon_helper import get_icon_button
from utils.setup_helper import safe_navigate
from utils.theme_manager import ThemeManager

class SettingsView(Screen):
    """Settings view screen."""
    
    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        # Initialize the settings_inputs dictionary first
        self.settings_inputs = {}
        self.config_manager = ConfigManager()
        
        # Set background color for the screen
        with self.canvas.before:
            Color(*ThemeManager.COLORS['background'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)
        
        # Create the main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Top bar with back button
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Back button with icon
        back_button = get_icon_button(
            ThemeManager.get_icon('back'),
            callback=self.go_back,
            tooltip="Back to Dashboard",
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        
        # Title
        title_label = Label(
            text="Settings",
            font_size=dp(24),
            bold=True,
            size_hint_x=1,
            color=ThemeManager.COLORS['text_primary']
        )
        
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        
        # Create scrollable content for settings
        scroll_view = ScrollView()
        settings_container = BoxLayout(orientation='vertical', spacing=dp(20), 
                                      size_hint_y=None, padding=(0, 0, 0, dp(20)))
        settings_container.bind(minimum_height=settings_container.setter('height'))
        
        # Set a background color for the settings container
        with settings_container.canvas.before:
            Color(*ThemeManager.COLORS['surface'])
            self.container_rect = Rectangle(pos=settings_container.pos, size=settings_container.size)
            settings_container.bind(pos=self._update_container_rect, size=self._update_container_rect)
        
        # Add the settings sections
        self._create_weather_settings(settings_container)
        self._create_calendar_settings(settings_container)
        self._create_display_settings(settings_container)
        self._create_device_settings(settings_container)
        
        # Add a Save Settings button at the bottom
        save_button = get_icon_button(
            ThemeManager.get_icon('save'),
            callback=self.save_settings,
            tooltip="Save Settings",
            text="Save Settings",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5}
        )
        
        # Add everything to the layout
        scroll_view.add_widget(settings_container)
        main_layout.add_widget(top_bar)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(save_button)
        self.add_widget(main_layout)
    
    def _update_bg_rect(self, instance, value):
        """Update the background rectangle position and size."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
    
    def _update_container_rect(self, instance, value):
        """Update the container rectangle position and size."""
        if hasattr(self, 'container_rect'):
            self.container_rect.pos = instance.pos
            self.container_rect.size = instance.size
    
    def go_back(self, instance):
        """Return to the main screen."""
        app = MDApp.get_running_app()
        safe_navigate('pdf_preview' if app.has_completed_setup else 'tablet_selection', transition_direction='right')
    
    def _create_section_header(self, title):
        """Create a section header with a title."""
        header_layout = BoxLayout(size_hint_y=None, height=dp(40))
        
        with header_layout.canvas.before:
            Color(*ThemeManager.COLORS['primary'], 0.2)  # Light primary color background
            self.rect = Rectangle(pos=header_layout.pos, size=header_layout.size)
            
        header_layout.bind(pos=self._update_rect, size=self._update_rect)
        
        label = Label(
            text=title,
            bold=True,
            font_size=ThemeManager.FONT_SIZES['h3'],
            color=ThemeManager.COLORS['text_primary']
        )
        header_layout.add_widget(label)
        
        return header_layout
    
    def _update_rect(self, instance, value):
        """Update the rectangle position and size."""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def _create_weather_settings(self, parent):
        """Create the weather API settings section."""
        # Section header
        parent.add_widget(self._create_section_header("Weather Settings"))
        
        # Settings grid
        weather_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # API Key
        weather_grid.add_widget(Label(text="OpenWeatherMap API Key:", halign='right', color=ThemeManager.COLORS['text_primary']))
        weather_api_key = TextInput(
            multiline=False,
            hint_text="Enter your API key",
            write_tab=False,
            text=self.config_manager.get_setting("weather", "api_key") or ""
        )
        self.settings_inputs['weather_api_key'] = weather_api_key
        weather_grid.add_widget(weather_api_key)
        
        # Location
        weather_grid.add_widget(Label(text="Location (city name):", halign='right', color=ThemeManager.COLORS['text_primary']))
        weather_location = TextInput(
            multiline=False,
            hint_text="e.g., London,UK",
            write_tab=False,
            text=self.config_manager.get_setting("weather", "location") or ""
        )
        self.settings_inputs['weather_location'] = weather_location
        weather_grid.add_widget(weather_location)
        
        parent.add_widget(weather_grid)
        
        # Add some info text about the weather API
        info_text = Label(
            text="Get your free API key at https://openweathermap.org/api",
            italic=True,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30),
            color=ThemeManager.COLORS['text_secondary']
        )
        parent.add_widget(info_text)
    
    def _create_calendar_settings(self, parent):
        """Create the calendar settings section."""
        # Section header
        parent.add_widget(self._create_section_header("Calendar Settings"))
        
        # URL input layout
        url_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        url_input = TextInput(
            hint_text="Enter iCal URL",
            multiline=False,
            write_tab=False
        )
        self.settings_inputs['new_calendar_url'] = url_input
        
        name_input = TextInput(
            hint_text="Calendar Name (optional)",
            multiline=False,
            write_tab=False,
            size_hint_x=0.4
        )
        self.settings_inputs['new_calendar_name'] = name_input
        
        add_button = get_icon_button(
            ThemeManager.get_icon('add'),
            callback=self.add_calendar,
            tooltip="Add Calendar",
            size_hint_x=None,
            width=dp(50)
        )
        
        url_layout.add_widget(url_input)
        url_layout.add_widget(name_input)
        url_layout.add_widget(add_button)
        parent.add_widget(url_layout)
        
        # Calendar list layout
        calendar_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        calendar_list_layout.bind(minimum_height=calendar_list_layout.setter('height'))
        self.settings_inputs['calendar_list'] = calendar_list_layout
        
        # Populate the calendar list
        self.update_calendar_list()
        
        # Add to parent
        parent.add_widget(calendar_list_layout)
    
    def _create_device_settings(self, parent):
        """Create the device settings section."""
        # Section header
        parent.add_widget(self._create_section_header("Device Settings"))
        
        # Device settings grid
        device_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Device name
        device_grid.add_widget(Label(text="Device Name:", halign='right', color=ThemeManager.COLORS['text_primary']))
        device_name = TextInput(
            multiline=False,
            hint_text="My reMarkable",
            write_tab=False,
            text=self.config_manager.get_setting("device", "name") or "My reMarkable"
        )
        self.settings_inputs['device_name'] = device_name
        device_grid.add_widget(device_name)
        
        # Device type selection
        device_grid.add_widget(Label(text="Device Type:", halign='right', color=ThemeManager.COLORS['text_primary']))
        device_type_layout = BoxLayout(spacing=dp(10))
        
        # Get current device type
        current_device_type = self.config_manager.get_setting("device", "type") or "reMarkable 2"
        
        # Create toggle buttons for device types
        rm1_button = ToggleButton(
            text="reMarkable 1",
            group="device_type",
            state='down' if current_device_type == "reMarkable 1" else 'normal'
        )
        rm2_button = ToggleButton(
            text="reMarkable 2",
            group="device_type",
            state='down' if current_device_type == "reMarkable 2" else 'normal'
        )
        rmpro_button = ToggleButton(
            text="Paper Pro",
            group="device_type",
            state='down' if current_device_type == "Paper Pro" else 'normal'
        )
        
        self.settings_inputs['device_type_buttons'] = {
            "reMarkable 1": rm1_button,
            "reMarkable 2": rm2_button,
            "Paper Pro": rmpro_button
        }
        
        device_type_layout.add_widget(rm1_button)
        device_type_layout.add_widget(rm2_button)
        device_type_layout.add_widget(rmpro_button)
        device_grid.add_widget(device_type_layout)
        
        parent.add_widget(device_grid)
    
    def _create_display_settings(self, parent):
        """Create the display settings section."""
        # Section header
        parent.add_widget(self._create_section_header("Display Settings"))
        
        # Display settings grid
        display_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Time format setting (24-hour vs 12-hour)
        display_grid.add_widget(Label(text="Time Format:", halign='right', color=ThemeManager.COLORS['text_primary']))
        time_format_layout = BoxLayout(spacing=dp(10))
        
        # Get current time format setting
        use_24h = self.config_manager.get_setting("display", "use_24h_time")
        use_24h = True if use_24h == "True" else False
        
        # Create toggle buttons for time format
        h12_button = ToggleButton(
            text="12-hour (AM/PM)",
            group="time_format",
            state='normal' if use_24h else 'down'
        )
        h24_button = ToggleButton(
            text="24-hour",
            group="time_format", 
            state='down' if use_24h else 'normal'
        )
        
        self.settings_inputs['time_format_buttons'] = {
            "12h": h12_button,
            "24h": h24_button
        }
        
        time_format_layout.add_widget(h12_button)
        time_format_layout.add_widget(h24_button)
        display_grid.add_widget(time_format_layout)
        
        # Week start setting (Monday vs Sunday)
        display_grid.add_widget(Label(text="Week Starts On:", halign='right', color=ThemeManager.COLORS['text_primary']))
        week_start_layout = BoxLayout(spacing=dp(10))
        
        # Get current week start setting
        monday_first = self.config_manager.get_setting("display", "monday_first")
        monday_first = True if monday_first == "True" else False
        
        # Create toggle buttons for week start
        sunday_button = ToggleButton(
            text="Sunday",
            group="week_start",
            state='normal' if monday_first else 'down'
        )
        monday_button = ToggleButton(
            text="Monday",
            group="week_start",
            state='down' if monday_first else 'normal'
        )
        
        self.settings_inputs['week_start_buttons'] = {
            "sunday": sunday_button,
            "monday": monday_button
        }
        
        week_start_layout.add_widget(sunday_button)
        week_start_layout.add_widget(monday_button)
        display_grid.add_widget(week_start_layout)
        
        parent.add_widget(display_grid)
    
    def update_calendar_list(self):
        """Update the list of calendars displayed in settings."""
        calendar_list = self.settings_inputs.get('calendar_list')
        if not calendar_list:
            return
            
        # Clear existing calendar entries
        calendar_list.clear_widgets()
        
        # Get calendars from config
        calendars = self.config_manager.get_calendars()
        
        if not calendars:
            calendar_list.add_widget(Label(
                text="No calendars added yet",
                italic=True,
                size_hint_y=None,
                height=dp(40),
                color=ThemeManager.COLORS['text_secondary']
            ))
            return
            
        # Create an entry for each calendar
        for i, calendar in enumerate(calendars):
            cal_entry = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
            
            # Calendar name/URL display
            cal_text = f"{calendar['name']}: {calendar['url']}"
            cal_label = Label(text=cal_text, halign='left', text_size=(None, None), color=ThemeManager.COLORS['text_primary'])
            
            # Remove button with icon
            remove_btn = get_icon_button(
                ThemeManager.get_icon('remove'),
                callback=partial(self.remove_calendar, calendar['url']),
                tooltip="Remove Calendar",
                size_hint_x=None,
                width=dp(40)
            )
            
            cal_entry.add_widget(cal_label)
            cal_entry.add_widget(remove_btn)
            calendar_list.add_widget(cal_entry)
            
        calendar_list.height = len(calendars) * dp(40)
    
    def add_calendar(self, instance):
        """Add a new calendar to the configuration."""
        url_input = self.settings_inputs.get('new_calendar_url')
        name_input = self.settings_inputs.get('new_calendar_name')
        
        if not url_input or not url_input.text:
            return
            
        url = url_input.text.strip()
        name = name_input.text.strip() if name_input and name_input.text else None
        
        if self.config_manager.add_calendar(url, name):
            # Clear the inputs
            url_input.text = ""
            if name_input:
                name_input.text = ""
                
            # Update the calendar list
            self.update_calendar_list()
    
    def remove_calendar(self, url, instance):
        """Remove a calendar from the configuration."""
        if self.config_manager.remove_calendar(url):
            # Update the calendar list
            self.update_calendar_list()
    
    def save_settings(self, instance):
        """Save all settings from the UI to the configuration."""
        try:
            # Show a loading indicator
            self._show_loading_popup("Saving settings...")
            
            # Schedule the actual save with a short delay
            Clock.schedule_once(lambda dt: self._perform_save_settings(), 0.1)
        except Exception as e:
            print(f"Error initiating settings save: {e}")
            self._show_error_popup(f"Could not save settings: {str(e)}")
    
    def _perform_save_settings(self):
        """Perform the actual settings save."""
        try:
            # Save weather settings
            weather_api_key = self.settings_inputs.get('weather_api_key')
            weather_location = self.settings_inputs.get('weather_location')
            
            if weather_api_key and weather_location:
                self.config_manager.set_weather_settings(
                    weather_api_key.text.strip(),
                    weather_location.text.strip()
                )
            
            # Save device settings
            device_name = self.settings_inputs.get('device_name')
            device_type_buttons = self.settings_inputs.get('device_type_buttons', {})
            
            if device_name:
                # Find the selected device type
                device_type = "reMarkable 2"  # default
                for type_name, button in device_type_buttons.items():
                    if button.state == 'down':
                        device_type = type_name
                        break
                
                self.config_manager.set_device_settings(
                    device_name.text.strip(),
                    device_type
                )
            
            # Save display settings
            time_format_buttons = self.settings_inputs.get('time_format_buttons', {})
            week_start_buttons = self.settings_inputs.get('week_start_buttons', {})
            
            use_24h = False
            for format_name, button in time_format_buttons.items():
                if button.state == 'down' and format_name == "24h":
                    use_24h = True
                    break
            
            monday_first = False
            for start_name, button in week_start_buttons.items():
                if button.state == 'down' and start_name == "monday":
                    monday_first = True
                    break
            
            self.config_manager.set_display_settings(
                use_24h,
                monday_first
            )
            
            # Update the UI to reflect any changes
            self.update_calendar_list()
            
            # Dismiss loading popup if it exists
            if hasattr(self, '_loading_popup') and self._loading_popup:
                self._loading_popup.dismiss()
                self._loading_popup = None
            
            # Notify the app that settings have changed
            app = MDApp.get_running_app()
            if hasattr(app, 'on_settings_changed'):
                app.on_settings_changed()
            
            # Show a popup confirmation
            popup = Popup(
                title='Settings Saved',
                content=Label(text='Your settings have been saved.', color=ThemeManager.COLORS['text_primary']),
                size_hint=(None, None),
                size=(dp(300), dp(150))
            )
            popup.open()
            
            # Auto-close after 2 seconds
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            if hasattr(self, '_loading_popup') and self._loading_popup:
                self._loading_popup.dismiss()
                self._loading_popup = None
            self._show_error_popup(f"Could not save settings: {str(e)}")
    
    def _show_loading_popup(self, message="Loading..."):
        """Show a loading popup."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, color=ThemeManager.COLORS['text_primary']))
        
        # Create and store the popup
        self._loading_popup = Popup(
            title='Please Wait',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(150)),
            auto_dismiss=False
        )
        self._loading_popup.open()
    
    def _show_error_popup(self, message):
        """Show an error popup."""
        popup = Popup(
            title='Error',
            content=Label(text=message, color=ThemeManager.COLORS['text_primary']),
            size_hint=(None, None),
            size=(dp(400), dp(200))
        )
        popup.open()
