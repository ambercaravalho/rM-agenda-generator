"""
Tablet selection screen for the reMarkable Agenda Generator.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.app import App

class TabletCard(BoxLayout):
    """Card display for a tablet option."""
    
    def __init__(self, model_name, description, image_path, supports_color, **kwargs):
        super(TabletCard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint = (None, None)
        self.size = (dp(250), dp(350))
        
        # Store model information
        self.model_name = model_name
        self.supports_color = supports_color
        
        # Create card content
        # Tablet image
        self.image = Image(
            source=image_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 0.6)
        )
        self.add_widget(self.image)
        
        # Model name
        self.name_label = Label(
            text=model_name,
            font_size=dp(18),
            bold=True,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.name_label)
        
        # Description
        self.desc_label = Label(
            text=description,
            font_size=dp(12),
            size_hint=(1, 0.2),
            text_size=(dp(230), None),
            halign='center',
            valign='top'
        )
        self.add_widget(self.desc_label)
        
        # Select button
        self.select_btn = Button(
            text="Select",
            size_hint=(0.8, 0.1)
        )
        self.select_btn.bind(on_press=self.on_select)
        self.add_widget(self.select_btn)
    
    def on_select(self, instance):
        """Handle selection of this tablet model."""
        app = App.get_running_app()
        app.set_tablet_model(self.model_name)

class TabletSelectionView(Screen):
    """Screen for selecting tablet model."""
    
    def __init__(self, **kwargs):
        super(TabletSelectionView, self).__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        title = Label(
            text="Select Your reMarkable Tablet Model",
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Description
        desc = Label(
            text="Choose your tablet model to optimize the PDF format",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(desc)
        
        # Cards container
        cards_container = GridLayout(
            cols=3,
            spacing=dp(30),
            padding=dp(20),
            size_hint_y=1
        )
        
        # Add tablet cards
        # reMarkable 1
        rm1_card = TabletCard(
            model_name="reMarkable 1",
            description="10.3\" E Ink display (1872×1404 pixels at 226 DPI)\nMonochrome\nOriginal model",
            image_path="assets/images/remarkable1.png",  # You'll need to add these images
            supports_color=False
        )
        cards_container.add_widget(rm1_card)
        
        # reMarkable 2
        rm2_card = TabletCard(
            model_name="reMarkable 2",
            description="10.3\" E Ink display (1872×1404 pixels at 226 DPI)\nMonochrome\nImproved latency and battery life",
            image_path="assets/images/remarkable2.png",
            supports_color=False
        )
        cards_container.add_widget(rm2_card)
        
        # Paper Pro (imaginary color version)
        paper_pro_card = TabletCard(
            model_name="Paper Pro",
            description="10.3\" E Ink Color display\nSupports color in PDF files\nExperimental features",
            image_path="assets/images/paperpro.png",
            supports_color=True
        )
        cards_container.add_widget(paper_pro_card)
        
        layout.add_widget(cards_container)
        
        self.add_widget(layout)
