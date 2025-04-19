"""
Configuration manager for the reMarkable Agenda Generator.
Handles loading, saving, and accessing settings.
"""
import os
import json
from kivy.app import App

class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = {
            "weather": {
                "api_key": "",
                "location": ""
            },
            "device": {
                "name": "My reMarkable",
                "type": "reMarkable 2"
            },
            "calendars": [],
            "display": {
                "use_24h_time": False,
                "monday_first": False
            }
        }
        
        # Load existing configuration if available
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        config_dir = self._get_config_dir()
        config_file = os.path.join(config_dir, "config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    
                    # Merge loaded config with defaults
                    if loaded_config.get("weather"):
                        self.config["weather"].update(loaded_config.get("weather", {}))
                    
                    if loaded_config.get("device"):
                        self.config["device"].update(loaded_config.get("device", {}))
                    
                    if loaded_config.get("calendars"):
                        self.config["calendars"] = loaded_config.get("calendars", [])
                        
                    if loaded_config.get("display"):
                        self.config["display"].update(loaded_config.get("display", {}))
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        config_dir = self._get_config_dir()
        
        # Make sure the directory exists
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        config_file = os.path.join(config_dir, "config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_setting(self, section, key):
        """Get a specific setting value."""
        if section in self.config and key in self.config[section]:
            return str(self.config[section][key])
        return None
    
    def set_weather_settings(self, api_key, location):
        """Set weather API settings."""
        self.config["weather"]["api_key"] = api_key
        self.config["weather"]["location"] = location
        return self.save_config()
    
    def set_device_settings(self, name, device_type):
        """Set device settings."""
        self.config["device"]["name"] = name
        self.config["device"]["type"] = device_type
        return self.save_config()
    
    def set_display_settings(self, use_24h_time, monday_first):
        """Set display settings for time format and week start."""
        self.config["display"]["use_24h_time"] = use_24h_time
        self.config["display"]["monday_first"] = monday_first
        return self.save_config()
    
    def get_calendars(self):
        """Get list of configured calendars."""
        return self.config.get("calendars", [])
    
    def add_calendar(self, url, name=None):
        """Add a calendar to the configuration."""
        if not url:
            return False
            
        # Generate a name if none provided
        if not name:
            name = f"Calendar {len(self.config['calendars']) + 1}"
        
        # Check if calendar with this URL already exists
        for cal in self.config['calendars']:
            if cal['url'] == url:
                return False
        
        # Add the calendar
        self.config['calendars'].append({
            'name': name,
            'url': url
        })
        
        return self.save_config()
    
    def remove_calendar(self, url):
        """Remove a calendar from the configuration."""
        if not url:
            return False
            
        # Find and remove the calendar
        for i, cal in enumerate(self.config['calendars']):
            if cal['url'] == url:
                self.config['calendars'].pop(i)
                return self.save_config()
        
        return False
    
    def _get_config_dir(self):
        """Get the configuration directory path."""
        # Use the app's directory structure
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")