"""
Helper functions for working with icons in the application.
Uses KivyMD's icons if available, or falls back to text buttons.
"""
from kivy.uix.button import Button
from kivy.metrics import dp

# Try to import KivyMD classes
try:
    from kivymd.uix.button import MDIconButton
    from kivymd.uix.tooltip import MDTooltip
    KIVYMD_AVAILABLE = True
    
    # Create a class that combines MDIconButton and MDTooltip
    class IconButtonWithTooltip(MDIconButton, MDTooltip):
        """Button with icon and tooltip."""
        pass
        
except ImportError:
    KIVYMD_AVAILABLE = False

def get_icon_button(icon_name, callback, tooltip=None, text=None, **kwargs):
    """
    Creates an icon button with optional tooltip and text.
    Falls back to a regular button with text if KivyMD is not available.
    
    Args:
        icon_name (str): The name of the icon to use (from Material Design icons)
        callback (callable): Function to call when button is pressed
        tooltip (str, optional): Text to show when hovering over the button
        text (str, optional): Text to display on the button (for fallback or alongside icon)
        **kwargs: Additional arguments to pass to the button constructor
    
    Returns:
        Button: A button widget
    """
    if KIVYMD_AVAILABLE:
        # Use KivyMD's icon button with tooltip
        if tooltip:
            button = IconButtonWithTooltip(
                icon=icon_name,
                on_release=callback,
                tooltip_text=tooltip,
                **kwargs
            )
        else:
            button = MDIconButton(
                icon=icon_name,
                on_release=callback,
                **kwargs
            )
        
        # If text is provided, set the text property (not all buttons support this)
        if text and hasattr(button, 'text'):
            button.text = text
            
        return button
    else:
        # Fall back to a regular button with text
        button_text = text or icon_name
        button = Button(
            text=button_text,
            on_press=callback,
            **kwargs
        )
        return button