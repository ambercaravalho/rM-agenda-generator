from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MainView(BoxLayout):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.label = Label(text='Welcome to the Kivy Desktop App!')
        self.add_widget(self.label)
        
        self.button = Button(text='Click Me')
        self.button.bind(on_press=self.on_button_click)
        self.add_widget(self.button)

    def on_button_click(self, instance):
        self.label.text = 'Button Clicked!'