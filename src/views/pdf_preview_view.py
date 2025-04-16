"""
PDF preview and generation functionality.
"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView

class PDFPreviewView(Screen):
    """PDF preview and generation screen."""
    
    def __init__(self, **kwargs):
        super(PDFPreviewView, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        layout.add_widget(Label(text="Generate PDF Calendar", size_hint_y=None, height=50))
        
        # Options
        options_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        month_btn = Button(text="Generate Month")
        month_btn.bind(on_press=lambda x: self.generate_pdf("month"))
        options_layout.add_widget(month_btn)
        
        week_btn = Button(text="Generate Week")
        week_btn.bind(on_press=lambda x: self.generate_pdf("week"))
        options_layout.add_widget(week_btn)
        
        day_btn = Button(text="Generate Day")
        day_btn.bind(on_press=lambda x: self.generate_pdf("day"))
        options_layout.add_widget(day_btn)
        
        layout.add_widget(options_layout)
        
        # File output selection
        layout.add_widget(Label(text="Select output location:", size_hint_y=None, height=30))
        
        self.file_chooser = FileChooserListView(path=os.path.expanduser("~"))
        layout.add_widget(self.file_chooser)
        
        # Back button
        back_btn = Button(text="Back to Calendar", size_hint_y=None, height=50)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def generate_pdf(self, view_type):
        """Generate a PDF for the specified view type."""
        output_path = self.file_chooser.path
        print(f"Generating {view_type} PDF to {output_path}")
        # Here you would call the PDF generation logic
        from utils.pdf_generator import generate_calendar_pdf
        pdf_file = generate_calendar_pdf(view_type, output_path)
        print(f"PDF generated: {pdf_file}")
    
    def go_back(self, instance):
        """Navigate back to the main screen."""
        self.manager.current = 'main'
