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
    
    # Start the application
    RemarkableAgendaApp().run()