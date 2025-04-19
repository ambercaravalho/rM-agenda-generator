"""
Theme manager for the reMarkable Agenda Generator.
Manages colors, fonts, and sizes across the application.
"""
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

class ThemeManager:
    """Static class to manage app theme settings."""
    
    # App color palette (using hex values for better compatibility)
    COLORS = {
        'primary': get_color_from_hex('#3388DD'),  # Blue
        'primary_light': get_color_from_hex('#66AAEE'),  # Light blue
        'accent': get_color_from_hex('#FF9933'),  # Orange
        'background': get_color_from_hex('#F5F5F5'),  # Light gray
        'surface': get_color_from_hex('#FFFFFF'),  # White
        'error': get_color_from_hex('#E53935'),  # Red
        'text_primary': get_color_from_hex('#212121'),  # Almost black
        'text_secondary': get_color_from_hex('#757575'),  # Dark gray
        'divider': get_color_from_hex('#BDBDBD'),  # Gray
        'card': get_color_from_hex('#FFFFFF'),  # White for cards
        'disabled': get_color_from_hex('#BDBDBD'),  # Gray for disabled elements
    }
    
    # Font sizes
    FONT_SIZES = {
        'h1': dp(24),
        'h2': dp(20),
        'h3': dp(18),
        'h4': dp(16),
        'body1': dp(14),
        'body2': dp(13),
        'caption': dp(12),
        'button': dp(14),
    }
    
    # Material Design icon names for common actions
    ICONS = {
        'back': 'arrow-left',
        'settings': 'cog',
        'save': 'content-save',
        'add': 'plus',
        'remove': 'close',
        'edit': 'pencil',
        'menu': 'menu',
        'close': 'close',
        'refresh': 'refresh',
        'calendar': 'calendar',
        'time': 'clock-outline',
        'device': 'tablet',
        'weather': 'weather-partly-cloudy',
        'pdf': 'file-pdf-box',
    }
    
    @staticmethod
    def get_color_rgba(color_name, alpha=1.0):
        """Get color with alpha."""
        if color_name in ThemeManager.COLORS:
            color = ThemeManager.COLORS[color_name]
            return (color[0], color[1], color[2], alpha)
        return (0, 0, 0, alpha)  # Default black
    
    @staticmethod
    def apply_theme_to_app(app):
        """Apply theme settings to the app."""
        # Apply theme to MDApp
        if hasattr(app, 'theme_cls'):
            # Instead of directly setting primary_color and accent_color which are readonly,
            # we use the appropriate KivyMD methods to set the theme colors
            
            # Set theme mode (light or dark)
            app.theme_cls.theme_style = 'Light'  # Use light theme by default
            
            # Use standard KivyMD color palettes
            # KivyMD uses predefined color palettes rather than custom RGB values
            app.theme_cls.primary_palette = 'Blue'  # Closest match to our blue
            app.theme_cls.accent_palette = 'Orange'  # Closest match to our orange
            
            # Optionally set hue if needed
            app.theme_cls.primary_hue = '500'  # Default material design shade
            app.theme_cls.accent_hue = '500'  # Default material design shade
    
    @staticmethod
    def get_icon(icon_name):
        """Get the appropriate icon name from the icons dictionary."""
        if icon_name in ThemeManager.ICONS:
            return ThemeManager.ICONS[icon_name]
        return icon_name  # Return the original name if not found