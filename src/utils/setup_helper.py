"""
Helper functions for setup and navigation across the application.
"""
from kivymd.app import MDApp

def safe_navigate(screen_name, transition_direction='left'):
    """
    Safely navigate to a screen by name.
    
    Args:
        screen_name (str): The name of the screen to navigate to
        transition_direction (str): The direction of the transition animation
    """
    app = MDApp.get_running_app()
    
    # Check if app is initialized
    if not app or not hasattr(app, 'screen_manager'):
        return False
    
    # Check if the requested screen exists
    if screen_name not in app.screen_manager.screen_names:
        return False
    
    # Set the transition direction
    if transition_direction in ('left', 'right', 'up', 'down'):
        app.screen_manager.transition.direction = transition_direction
    
    # Change to the requested screen
    app.screen_manager.current = screen_name
    return True