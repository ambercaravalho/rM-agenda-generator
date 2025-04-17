"""
PDF preview and generation functionality.
"""
import os
import tempfile
from datetime import datetime, timedelta
import threading

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.window import Window

from utils.pdf_generator import generate_calendar_pdf
from pdf2image import convert_from_path

class PDFPreviewView(Screen):
    """PDF preview and generation screen."""
    
    preview_image = ObjectProperty(None)
    temp_pdf_path = StringProperty('')
    
    def __init__(self, **kwargs):
        super(PDFPreviewView, self).__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # Left panel (Calendar options)
        left_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_x=0.25
        )
        
        # Title of left panel
        left_panel.add_widget(Label(
            text="Calendar Options",
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))
        
        # Calendar type selector
        left_panel.add_widget(Label(
            text="Calendar Type",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        # Calendar type buttons
        type_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(150)
        )
        
        self.month_btn = Button(text="Month View", size_hint_y=None, height=dp(40))
        self.month_btn.bind(on_press=lambda x: self.update_view_type('month'))
        
        self.week_btn = Button(text="Week View", size_hint_y=None, height=dp(40))
        self.week_btn.bind(on_press=lambda x: self.update_view_type('week'))
        
        self.day_btn = Button(text="Day View", size_hint_y=None, height=dp(40))
        self.day_btn.bind(on_press=lambda x: self.update_view_type('day'))
        
        type_layout.add_widget(self.month_btn)
        type_layout.add_widget(self.week_btn)
        type_layout.add_widget(self.day_btn)
        
        left_panel.add_widget(type_layout)
        left_panel.add_widget(Label(size_hint_y=None, height=dp(20)))  # Spacer
        
        # Include elements section
        left_panel.add_widget(Label(
            text="Include Elements",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        # Checkboxes for additional elements would go here
        # (Weather, Tasks, Notes, etc.)
        
        # Back button at the bottom
        back_btn = Button(
            text="Back to Calendar",
            size_hint_y=None,
            height=dp(50)
        )
        back_btn.bind(on_press=self.go_back)
        
        # Add a spacer to push the back button to the bottom
        left_panel.add_widget(Label(size_hint_y=1))
        left_panel.add_widget(back_btn)
        
        # Center panel (PDF Preview)
        center_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_x=0.5
        )
        
        # Title for preview
        preview_header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        preview_header.add_widget(Label(
            text="PDF Preview",
            font_size=dp(20),
            bold=True
        ))
        
        # Information about the current view
        self.info_label = Label(
            text="",
            font_size=dp(14),
            halign='right',
            valign='middle',
            size_hint_x=0.5
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        preview_header.add_widget(self.info_label)
        
        center_panel.add_widget(preview_header)
        
        # PDF Preview image with border
        preview_container = BoxLayout(
            padding=dp(2),
            orientation='vertical'
        )
        
        # Draw a border around the preview
        with preview_container.canvas.before:
            from kivy.graphics import Color, Line
            Color(0.7, 0.7, 0.7, 1)
            self.border = Line(rectangle=(0, 0, 0, 0), width=2)
            
        def update_border(instance, value):
            self.border.rectangle = (
                instance.x, instance.y, instance.width, instance.height
            )
            
        preview_container.bind(pos=update_border, size=update_border)
        
        self.preview_image = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1)
        )
        preview_container.add_widget(self.preview_image)
        center_panel.add_widget(preview_container)
        
        # Right panel (Generation options)
        right_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_x=0.25
        )
        
        # Title of right panel
        right_panel.add_widget(Label(
            text="Generation Options",
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))
        
        # Selected tablet info
        self.tablet_info = Label(
            text="Tablet: Not Selected",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        right_panel.add_widget(self.tablet_info)
        
        # Output location
        right_panel.add_widget(Label(
            text="Save Location:",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser("~/Documents"),
            size_hint_y=0.6
        )
        right_panel.add_widget(self.file_chooser)
        
        # Filename input would go here
        
        # Generate button
        self.generate_btn = Button(
            text="Generate PDF",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.generate_btn.bind(on_press=self.generate_final_pdf)
        
        # Add a spacer to push the generate button to the bottom
        right_panel.add_widget(Label(size_hint_y=0.2))
        right_panel.add_widget(self.generate_btn)
        
        # Add panels to main layout
        layout.add_widget(left_panel)
        layout.add_widget(center_panel)
        layout.add_widget(right_panel)
        
        self.add_widget(layout)
        
        # Initialize view properties
        self.view_type = 'month'
        self.current_date = datetime.now()
        self.tablet_model = None
        self.events = None
        self.weather = None
        self.tasks = None
    
    def set_view_data(self, view_type, date, tablet_model, events=None, weather=None, tasks=None):
        """Set the view data and generate a preview."""
        self.view_type = view_type
        self.current_date = date
        self.tablet_model = tablet_model
        self.events = events or {}
        self.weather = weather or {}
        self.tasks = tasks or []
        
        # Update UI elements
        self.tablet_info.text = f"Tablet: {self.tablet_model}"
        self.info_label.text = f"{self._get_view_type_name()} | {self._format_date()}"
        
        # Highlight the active view button
        for btn in [self.month_btn, self.week_btn, self.day_btn]:
            btn.background_color = (1, 1, 1, 1)  # Reset all
            
        if self.view_type == 'month':
            self.month_btn.background_color = (0.6, 0.8, 1, 1)
        elif self.view_type == 'week':
            self.week_btn.background_color = (0.6, 0.8, 1, 1)
        elif self.view_type == 'day':
            self.day_btn.background_color = (0.6, 0.8, 1, 1)
        
        # Generate the preview in a separate thread
        Clock.schedule_once(lambda dt: self.generate_preview(), 0.1)
    
    def _get_view_type_name(self):
        """Get a formatted name for the current view type."""
        if self.view_type == 'month':
            return "Monthly Calendar"
        elif self.view_type == 'week':
            return "Weekly Planner"
        elif self.view_type == 'day':
            return "Daily Agenda"
        return "Calendar"
    
    def _format_date(self):
        """Format the date information based on view type."""
        if self.view_type == 'month':
            return self.current_date.strftime("%B %Y")
        elif self.view_type == 'week':
            # Calculate week start and end
            start_date = self.current_date - timedelta(days=self.current_date.weekday())
            end_date = start_date + timedelta(days=6)
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        elif self.view_type == 'day':
            return self.current_date.strftime("%A, %B %d, %Y")
        return ""
    
    def update_view_type(self, view_type):
        """Change the current view type and regenerate preview."""
        if view_type != self.view_type:
            self.view_type = view_type
            self.info_label.text = f"{self._get_view_type_name()} | {self._format_date()}"
            self.generate_preview()
            
            # Update button highlights
            for btn in [self.month_btn, self.week_btn, self.day_btn]:
                btn.background_color = (1, 1, 1, 1)  # Reset all
                
            if view_type == 'month':
                self.month_btn.background_color = (0.6, 0.8, 1, 1)
            elif view_type == 'week':
                self.week_btn.background_color = (0.6, 0.8, 1, 1)
            elif view_type == 'day':
                self.day_btn.background_color = (0.6, 0.8, 1, 1)
    
    def generate_preview(self):
        """Generate a PDF preview."""
        # Create a temporary file for the preview PDF
        try:
            # Create temp directory if it doesn't exist
            temp_dir = tempfile.mkdtemp()
            self.temp_pdf_path = os.path.join(temp_dir, f"preview_{self.view_type}.pdf")
            
            # Show loading indicator
            self.show_loading_popup("Generating preview...")
            
            # Generate the PDF in a separate thread
            threading.Thread(target=self._generate_pdf_thread).start()
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            self.dismiss_loading_popup()
    
    def _generate_pdf_thread(self):
        """Generate PDF in a background thread."""
        try:
            # Generate the PDF
            generate_calendar_pdf(
                self.view_type,
                os.path.dirname(self.temp_pdf_path),
                date=self.current_date,
                events=self.events,
                weather=self.weather,
                tasks=self.tasks
            )
            
            # Convert to image for preview
            self._convert_pdf_to_image()
            
        except Exception as e:
            print(f"Error in PDF generation: {e}")
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self.dismiss_loading_popup(), 0)
    
    def _convert_pdf_to_image(self):
        """Convert the PDF to an image for preview."""
        try:
            # Check if file exists
            if not os.path.exists(self.temp_pdf_path):
                print(f"PDF file not found: {self.temp_pdf_path}")
                Clock.schedule_once(lambda dt: self.dismiss_loading_popup(), 0)
                return
            
            # Convert the first page of the PDF to an image
            images = convert_from_path(self.temp_pdf_path, dpi=100, first_page=1, last_page=1)
            
            if images and len(images) > 0:
                # Save the image to a temporary file
                temp_img_path = self.temp_pdf_path.replace('.pdf', '.png')
                images[0].save(temp_img_path, 'PNG')
                
                # Update the UI image in the main thread
                Clock.schedule_once(lambda dt: self._update_preview_image(temp_img_path), 0)
            else:
                Clock.schedule_once(lambda dt: self.dismiss_loading_popup(), 0)
                
        except Exception as e:
            print(f"PDF conversion error: {e}")
            # Schedule UI update on main thread
            Clock.schedule_once(lambda dt: self.dismiss_loading_popup(), 0)
    
    def _update_preview_image(self, image_path):
        """Update the preview image (called on main thread)."""
        if os.path.exists(image_path):
            self.preview_image.source = image_path
            self.preview_image.reload()
            
        # Dismiss the loading popup
        self.dismiss_loading_popup()
    
    def generate_final_pdf(self, instance):
        """Generate the final PDF file at the selected location."""
        if not self.file_chooser.path:
            self.show_alert_popup("Please select an output directory first.")
            return
        
        output_path = self.file_chooser.path
        
        # Show loading indicator
        self.show_loading_popup("Generating PDF...")
        
        # Generate in separate thread
        threading.Thread(target=lambda: self._generate_final_pdf_thread(output_path)).start()
    
    def _generate_final_pdf_thread(self, output_path):
        """Generate the final PDF in a background thread."""
        try:
            pdf_file = generate_calendar_pdf(
                self.view_type,
                output_path,
                date=self.current_date,
                events=self.events,
                weather=self.weather,
                tasks=self.tasks
            )
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._show_success_popup(pdf_file), 0)
            
        except Exception as e:
            print(f"Error generating final PDF: {e}")
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self.show_alert_popup(f"Error generating PDF: {e}"), 0)
    
    def _show_success_popup(self, pdf_file):
        """Show a success popup with the path to the generated PDF."""
        self.dismiss_loading_popup()
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text=f"PDF successfully generated!",
            font_size=dp(16)
        ))
        
        # Truncate path if too long for display
        display_path = pdf_file
        if len(pdf_file) > 60:
            display_path = "..." + pdf_file[-57:]
            
        content.add_widget(Label(
            text=f"Location: {display_path}",
            font_size=dp(14)
        ))
        
        # Done button
        btn = Button(text="Done", size_hint_y=None, height=dp(40))
        content.add_widget(btn)
        
        popup = Popup(
            title="Success",
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        
        # Bind the button to close the popup
        btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def show_loading_popup(self, message="Loading..."):
        """Show a loading popup with a progress indicator."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=message,
            font_size=dp(16)
        ))
        content.add_widget(ProgressBar(
            max=100,
            value=40,
            size_hint_y=None,
            height=dp(30)
        ))
        
        self.loading_popup = Popup(
            title="Processing",
            content=content,
            size_hint=(0.5, 0.25),
            auto_dismiss=False
        )
        self.loading_popup.open()
    
    def dismiss_loading_popup(self):
        """Dismiss the loading popup if it exists."""
        if hasattr(self, 'loading_popup') and self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None
    
    def show_alert_popup(self, message):
        """Show an alert popup with the given message."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text=message,
            font_size=dp(16)
        ))
        
        # OK button
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        content.add_widget(btn)
        
        popup = Popup(
            title="Alert",
            content=content,
            size_hint=(0.5, 0.3),
            auto_dismiss=True
        )
        
        # Bind the button to close the popup
        btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def go_back(self, instance):
        """Navigate back to the calendar screen."""
        self.manager.current = 'calendar'
    
    def on_leave(self):
        """Cleanup temporary files when leaving the screen."""
        super().on_leave()
        try:
            # Remove the temporary PDF file
            if os.path.exists(self.temp_pdf_path):
                os.remove(self.temp_pdf_path)
            
            # Remove the temporary image file
            temp_img_path = self.temp_pdf_path.replace('.pdf', '.png')
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            
            # Remove temp directory if empty
            temp_dir = os.path.dirname(self.temp_pdf_path)
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
                
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
