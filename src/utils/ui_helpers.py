"""
UI helper functions and classes for the reMarkable Agenda Generator.
"""
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.clock import Clock

def create_safe_label(text, **kwargs):
    """
    Create a Label with safe text_size handling to avoid the 'text_size' error.
    
    Args:
        text: The text to display in the label
        **kwargs: Additional keyword arguments to pass to the Label constructor
    
    Returns:
        A Label widget with safe text_size handling
    """
    # Create a wrapper layout to constrain the label
    layout = BoxLayout(orientation='vertical')
    
    # Set defaults for text alignment
    if 'halign' not in kwargs:
        kwargs['halign'] = 'left'
    if 'valign' not in kwargs:
        kwargs['valign'] = 'middle'
    
    # Create the label
    label = Label(text=text, **kwargs)
    
    # Set text_size safely after creation
    def update_text_size(instance, size):
        try:
            # Use size of parent widget to define text wrapping
            label.text_size = (size[0], None)
        except Exception as e:
            print(f"Text size update error (non-fatal): {e}")
    
    # Bind size updates to text_size updates
    layout.bind(size=update_text_size)
    layout.add_widget(label)
    
    # Trigger an initial text_size update
    Clock.schedule_once(lambda dt: update_text_size(layout, layout.size), 0.1)
    
    return layout

class SafeLabel(BoxLayout):
    """A label with safe text_size handling to avoid the 'text_size' error."""
    
    def __init__(self, text="", **kwargs):
        # Extract label-specific kwargs
        label_kwargs = {
            'halign': kwargs.pop('halign', 'left'),
            'valign': kwargs.pop('valign', 'middle'),
            'font_size': kwargs.pop('font_size', dp(14)),
            'bold': kwargs.pop('bold', False),
            'italic': kwargs.pop('italic', False),
            'color': kwargs.pop('color', [1, 1, 1, 1]),
            'markup': kwargs.pop('markup', False),
        }
        
        # Initialize the BoxLayout
        super(SafeLabel, self).__init__(orientation='vertical', **kwargs)
        
        # Create the label with try-except to handle potential errors
        try:
            self.label = Label(text=text, **label_kwargs)
            self.add_widget(self.label)
            
            # Bind size updates to text_size updates
            self.bind(size=self._update_text_size)
            
            # Trigger an initial text_size update
            Clock.schedule_once(lambda dt: self._update_text_size(self, self.size), 0.1)
        except Exception as e:
            print(f"SafeLabel creation error (non-fatal): {e}")
            # Create a fallback label if there's an error
            self.label = Label(text=text)
            self.add_widget(self.label)
    
    def _update_text_size(self, instance, size):
        """Update the label's text_size safely."""
        try:
            if hasattr(self, 'label'):
                self.label.text_size = (size[0], None)
        except Exception as e:
            print(f"SafeLabel._update_text_size error (non-fatal): {e}")
    
    @property
    def text(self):
        """Get the label text safely."""
        try:
            return self.label.text if hasattr(self, 'label') else ""
        except Exception:
            return ""
    
    @text.setter
    def text(self, value):
        """Set the label text safely."""
        try:
            if hasattr(self, 'label'):
                self.label.text = value
        except Exception as e:
            print(f"SafeLabel.text setter error (non-fatal): {e}")
