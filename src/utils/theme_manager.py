"""
Theme manager for the reMarkable Agenda Generator.
Manages colors, fonts, and sizes across the application.
"""
from kivy.metrics import dp

class ThemeManager:
    """Static class to manage app theme settings."""
    
    # App color palette
    COLORS = {
        'primary': (0.2, 0.6, 0.9),  # Blue
        'primary_light': (0.4, 0.7, 0.95),  # Light blue
        'accent': (0.95, 0.6, 0.1),  # Orange
        'background': (0.95, 0.95, 0.95),  # Light gray
        'surface': (1, 1, 1),  # White
        'error': (0.9, 0.2, 0.2),  # Red
        'text_primary': (0.1, 0.1, 0.1),  # Almost black
        'text_secondary': (0.4, 0.4, 0.4),  # Dark gray
        'divider': (0.8, 0.8, 0.8),  # Gray
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
        # This method can be expanded to apply theme settings to the app
        pass