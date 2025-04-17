"""
Entry point for the reMarkable Agenda Generator application.
"""
import os
import sys
from kivy.config import Config

# Configure Kivy before other imports
# Allow resizing but with constraints to prevent size-related errors
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# Start with a reasonable window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
# Allow resizing but set min/max constraints to avoid layout issues
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')
# Set a visible window state
Config.set('graphics', 'window_state', 'visible')
# Enable resizing
Config.set('graphics', 'resizable', '1')
# Use SDL2 window provider if available, else fall back to others
Config.set('kivy', 'window_backend', 'sdl2,pygame,x11')

# Now import Kivy-related modules
from app import RemarkableAgendaApp
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.core.window import Window

class KivyExceptionHandler(ExceptionHandler):
    """Enhanced exception handler for Kivy with comprehensive recovery mechanisms."""
    def handle_exception(self, exception):
        # Print the exception for debugging
        print(f"Exception caught: {type(exception).__name__}: {exception}")
        
        # Handle specific errors with tailored recovery approaches
        exception_str = str(exception)
        
        # SDL2 window errors
        if "SDL2" in exception_str or "_WindowSDL2Storage" in exception_str:
            print("Caught SDL2 error, attempting recovery...")
            return True
            
        # Text size related errors    
        elif "'text_size'" in exception_str:
            print("Caught text_size error, attempting recovery...")
            return True
            
        # Texture errors often from image loading
        elif "'texture'" in exception_str:
            print("Caught texture error, attempting recovery...")
            return True
            
        # Screen manager transition errors
        elif "ScreenManager" in exception_str or "Screen" in exception_str:
            print("Caught screen transition error, attempting recovery...")
            return True
            
        # Layout update errors
        elif "layout" in exception_str.lower() or "widget" in exception_str.lower():
            print("Caught layout error, attempting recovery...")
            return True
            
        # Let Python handle other exceptions normally
        return ExceptionHandler.handle_exception(self, exception)

# Register the enhanced exception handler
ExceptionManager.add_handler(KivyExceptionHandler())

if __name__ == "__main__":
    # Add the parent directory to sys.path to allow importing modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    # Set the current directory to src to help with imports
    os.chdir(current_dir)
    
    # Create necessary directories if they don't exist
    assets_dir = os.path.join(current_dir, "assets")
    images_dir = os.path.join(assets_dir, "images")
    output_dir = os.path.join(current_dir, "output")
    temp_dir = os.path.join(assets_dir, "temp")
    
    for directory in [assets_dir, images_dir, output_dir, temp_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Create placeholder image if it doesn't exist
    placeholder_path = os.path.join(images_dir, "device_placeholder.png")
    if not os.path.exists(placeholder_path):
        try:
            # Generate a simple placeholder image using PIL if available
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (300, 400), color=(240, 240, 240))
                draw = ImageDraw.Draw(img)
                draw.rectangle([50, 50, 250, 350], outline=(200, 200, 200), width=2)
                draw.text((100, 200), "Device Image", fill=(150, 150, 150))
                img.save(placeholder_path)
                print(f"Created placeholder image at {placeholder_path}")
            except ImportError:
                print("PIL not available, skipping placeholder image creation")
        except Exception as e:
            print(f"Could not create placeholder image: {e}")
    
    # Create PDF preview placeholder image if it doesn't exist
    preview_placeholder_path = os.path.join(images_dir, "preview_placeholder.png")
    if not os.path.exists(preview_placeholder_path):
        try:
            # Generate a simple placeholder image using PIL if available
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (600, 800), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                draw.rectangle([10, 10, 590, 790], outline=(100, 100, 100), width=2)
                
                # Try to use a default font or fall back to default
                try:
                    font = ImageFont.truetype("Arial", 24)
                except:
                    font = ImageFont.load_default()
                
                draw.text((300, 400), "PDF Preview", fill=(100, 100, 100), 
                          anchor="mm", font=font)
                img.save(preview_placeholder_path)
                print(f"Created PDF preview placeholder image at {preview_placeholder_path}")
            except ImportError:
                print("PIL not available, skipping preview placeholder image creation")
        except Exception as e:
            print(f"Could not create PDF preview placeholder image: {e}")
    
    try:
        # Set up window event handling before app starts
        def on_resize(*args):
            """Handle window resize events safely."""
            print(f"Window resized: {Window.width}x{Window.height}")
            try:
                # Trigger layout updates if app is running
                app = RemarkableAgendaApp.get_running_app()
                if app:
                    # Request a delayed layout update to avoid mid-transition issues
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: app.update_layouts(), 0.1)
            except Exception as e:
                print(f"Resize handler error (non-fatal): {e}")
                
        Window.bind(on_resize=on_resize)
                
        # Start the application with error handling
        app = RemarkableAgendaApp()
        app.run()
    except Exception as e:
        print(f"Application crashed with error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Try running with a different graphics backend:")
        print("   KIVY_GL_BACKEND=sdl2 python src/main.py")
        print("2. Make sure you have the latest SDL2 libraries installed")
        print("3. If you're using a virtual environment, ensure Kivy is properly installed")
        print("4. Try with default settings and no window customization:")
        print("   python -m pip install --upgrade kivy")
        print("   python src/main.py --debug")