"""
Entry point for the reMarkable Agenda Generator application.
"""
import os
import sys
from app import RemarkableAgendaApp

if __name__ == "__main__":
    # Add the parent directory to sys.path to allow importing modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    # Set the current directory to src to help with imports
    os.chdir(current_dir)
    
    # Create assets directories if they don't exist
    assets_dir = os.path.join(current_dir, "assets")
    images_dir = os.path.join(assets_dir, "images")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # Start the application
    RemarkableAgendaApp().run()