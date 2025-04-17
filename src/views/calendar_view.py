"""
Calendar view screen for the reMarkable Agenda Generator.
"""
from datetime import datetime, timedelta
import calendar

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.app import App

class CalendarHeader(BoxLayout):
    """Header for the calendar view with navigation controls."""
    
    def __init__(self, parent_view, **kwargs):
        super(CalendarHeader, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [10, 5]
        self.spacing = 10
        
        # Previous button
        self.prev_button = Button(
            text="<",
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.prev_button.bind(on_press=self.parent_view.previous_period)
        
        # Today button
        self.today_button = Button(
            text="Today",
            size_hint=(None, None),
            size=(dp(80), dp(40))
        )
        self.today_button.bind(on_press=self.parent_view.go_to_today)
        
        # Title label (month/year or week range)
        self.title_label = Label(
            text="",
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(40)
        )
        
        # Next button
        self.next_button = Button(
            text=">",
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.next_button.bind(on_press=self.parent_view.next_period)
        
        # Preview PDF button
        self.pdf_button = Button(
            text="Preview PDF",
            size_hint=(None, None),
            size=(dp(120), dp(40))
        )
        self.pdf_button.bind(on_press=self.parent_view.show_pdf_preview)
        
        # Add widgets to layout
        self.add_widget(self.prev_button)
        self.add_widget(self.today_button)
        self.add_widget(self.title_label)
        self.add_widget(self.next_button)
        self.add_widget(self.pdf_button)

class MonthView(BoxLayout):
    """Month calendar view."""
    
    def __init__(self, parent_view, **kwargs):
        super(MonthView, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.orientation = 'vertical'
        
        # Month header
        self.header = CalendarHeader(parent_view)
        self.add_widget(self.header)
        
        # Month grid
        self.grid = GridLayout(cols=7, spacing=2, size_hint_y=1)
        self.add_widget(self.grid)
        
        # Set the current date
        self.current_date = datetime.now()
        self.update_calendar()
    
    def update_calendar(self):
        """Update the calendar grid based on the current month."""
        self.grid.clear_widgets()
        
        # Update header title
        self.header.title_label.text = self.current_date.strftime("%B %Y")
        
        # Add day name headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day_name in day_names:
            day_label = Label(text=day_name, size_hint_y=None, height=dp(30))
            with day_label.canvas.before:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=day_label.pos, size=day_label.size)
            self.grid.add_widget(day_label)
        
        # Get the calendar for current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Add day buttons to the grid
        for week in cal:
            for day in week:
                if day == 0:
                    # Empty cell for days not in this month
                    self.grid.add_widget(Label(text=""))
                else:
                    btn = Button(text=str(day))
                    
                    # Highlight current day
                    if (day == datetime.now().day and 
                        self.current_date.month == datetime.now().month and 
                        self.current_date.year == datetime.now().year):
                        btn.background_color = (0.6, 0.8, 1, 1)
                    
                    # Bind button to day selection
                    btn.bind(on_press=lambda instance, day=day: self.parent_view.select_day(day))
                    
                    self.grid.add_widget(btn)

class WeekView(BoxLayout):
    """Week calendar view."""
    
    def __init__(self, parent_view, **kwargs):
        super(WeekView, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.orientation = 'vertical'
        
        # Week header
        self.header = CalendarHeader(parent_view)
        self.add_widget(self.header)
        
        # Week grid (hours x days)
        self.scroll_view = ScrollView()
        self.grid = GridLayout(cols=8, spacing=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll_view.add_widget(self.grid)
        self.add_widget(self.scroll_view)
        
        # Set the current date to the beginning of the week
        self.current_date = datetime.now()
        self.start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        self.update_calendar()
    
    def update_calendar(self):
        """Update the week view grid."""
        self.grid.clear_widgets()
        
        # Calculate start and end of the week
        self.start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = self.start_of_week + timedelta(days=6)
        
        # Update header title
        self.header.title_label.text = f"{self.start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
        
        # Add time column header
        self.grid.add_widget(Label(text="Time", size_hint_y=None, height=dp(40)))
        
        # Add day headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            day_date = self.start_of_week + timedelta(days=i)
            header_text = f"{day_name}\n{day_date.day}"
            day_header = Label(text=header_text, size_hint_y=None, height=dp(40))
            
            # Highlight current day
            if day_date.date() == datetime.now().date():
                with day_header.canvas.before:
                    Color(0.6, 0.8, 1, 1)
                    Rectangle(pos=day_header.pos, size=day_header.size)
            
            self.grid.add_widget(day_header)
        
        # Add hour rows
        for hour in range(8, 21):  # 8 AM to 8 PM
            # Hour label
            hour_label = Label(text=f"{hour}:00", size_hint_y=None, height=dp(60))
            self.grid.add_widget(hour_label)
            
            # Day cells for this hour
            for day in range(7):
                cell = Button(text="", size_hint_y=None, height=dp(60))
                # Bind to select day and hour
                cell.bind(on_press=lambda instance, day=day, hour=hour: 
                          self.parent_view.select_time_slot(day, hour))
                self.grid.add_widget(cell)

class DayView(BoxLayout):
    """Day calendar view."""
    
    def __init__(self, parent_view, **kwargs):
        super(DayView, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.orientation = 'vertical'
        
        # Day header
        self.header = CalendarHeader(parent_view)
        self.add_widget(self.header)
        
        # Day schedule
        self.scroll_view = ScrollView()
        self.schedule = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.schedule.bind(minimum_height=self.schedule.setter('height'))
        self.scroll_view.add_widget(self.schedule)
        self.add_widget(self.scroll_view)
        
        # Set the current date
        self.current_date = datetime.now()
        self.update_calendar()
    
    def update_calendar(self):
        """Update the day view schedule."""
        self.schedule.clear_widgets()
        
        # Update header title
        self.header.title_label.text = self.current_date.strftime("%A, %B %d, %Y")
        
        # Add hour slots
        for hour in range(8, 21):  # 8 AM to 8 PM
            hour_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
            
            # Time label
            time_label = Label(text=f"{hour}:00", size_hint_x=None, width=dp(60))
            hour_layout.add_widget(time_label)
            
            # Event button (placeholder for now)
            event_button = Button(text="")
            hour_layout.add_widget(event_button)
            
            self.schedule.add_widget(hour_layout)

class CalendarView(Screen):
    """Calendar view screen with tabs for month, week, and day views."""
    
    def __init__(self, **kwargs):
        super(CalendarView, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical')
        
        # Show selected tablet model
        self.tablet_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.tablet_label = Label(text="Selected Tablet: ", size_hint_x=None, width=dp(150))
        self.tablet_model = Label(text="", size_hint_x=1)
        self.tablet_info.add_widget(self.tablet_label)
        self.tablet_info.add_widget(self.tablet_model)
        self.layout.add_widget(self.tablet_info)
        
        # Create the tabbed panel
        self.tabs = TabbedPanel(do_default_tab=False, size_hint=(1, 1))
        
        # Month tab
        month_tab = TabbedPanelItem(text='Month')
        self.month_view = MonthView(self)
        month_tab.add_widget(self.month_view)
        self.tabs.add_widget(month_tab)
        
        # Week tab
        week_tab = TabbedPanelItem(text='Week')
        self.week_view = WeekView(self)
        week_tab.add_widget(self.week_view)
        self.tabs.add_widget(week_tab)
        
        # Day tab
        day_tab = TabbedPanelItem(text='Day')
        self.day_view = DayView(self)
        day_tab.add_widget(self.day_view)
        self.tabs.add_widget(day_tab)
        
        # Set default tab
        self.tabs.default_tab = month_tab
        
        self.layout.add_widget(self.tabs)
        self.add_widget(self.layout)
        
        # Set the current view
        self.current_view = 'month'
    
    def on_enter(self):
        """Called when the screen is entered."""
        app = App.get_running_app()
        self.tablet_model.text = app.tablet_model or "Not selected"
    
    def previous_period(self, instance):
        """Go to previous month/week/day."""
        if self.current_view == 'month':
            # Go to previous month
            if self.month_view.current_date.month == 1:
                self.month_view.current_date = self.month_view.current_date.replace(
                    year=self.month_view.current_date.year - 1, month=12)
            else:
                self.month_view.current_date = self.month_view.current_date.replace(
                    month=self.month_view.current_date.month - 1)
            self.month_view.update_calendar()
        
        elif self.current_view == 'week':
            # Go to previous week
            self.week_view.current_date -= timedelta(days=7)
            self.week_view.update_calendar()
        
        elif self.current_view == 'day':
            # Go to previous day
            self.day_view.current_date -= timedelta(days=1)
            self.day_view.update_calendar()
    
    def next_period(self, instance):
        """Go to next month/week/day."""
        if self.current_view == 'month':
            # Go to next month
            if self.month_view.current_date.month == 12:
                self.month_view.current_date = self.month_view.current_date.replace(
                    year=self.month_view.current_date.year + 1, month=1)
            else:
                self.month_view.current_date = self.month_view.current_date.replace(
                    month=self.month_view.current_date.month + 1)
            self.month_view.update_calendar()
        
        elif self.current_view == 'week':
            # Go to next week
            self.week_view.current_date += timedelta(days=7)
            self.week_view.update_calendar()
        
        elif self.current_view == 'day':
            # Go to next day
            self.day_view.current_date += timedelta(days=1)
            self.day_view.update_calendar()
    
    def go_to_today(self, instance):
        """Go to today's date."""
        today = datetime.now()
        
        if self.current_view == 'month':
            self.month_view.current_date = today
            self.month_view.update_calendar()
        
        elif self.current_view == 'week':
            self.week_view.current_date = today
            self.week_view.update_calendar()
        
        elif self.current_view == 'day':
            self.day_view.current_date = today
            self.day_view.update_calendar()
    
    def select_day(self, day):
        """Select a specific day from the month view."""
        # Switch to day view with the selected date
        selected_date = self.month_view.current_date.replace(day=day)
        self.day_view.current_date = selected_date
        self.day_view.update_calendar()
        self.tabs.switch_to(self.tabs.tab_list[2])  # Switch to day tab
        self.current_view = 'day'
    
    def select_time_slot(self, day, hour):
        """Select a specific time slot from the week view."""
        # Calculate the date for the selected day
        selected_date = self.week_view.start_of_week + timedelta(days=day)
        self.day_view.current_date = selected_date
        self.day_view.update_calendar()
        self.tabs.switch_to(self.tabs.tab_list[2])  # Switch to day tab
        self.current_view = 'day'
    
    def show_pdf_preview(self, instance):
        """Show the PDF preview screen."""
        app = App.get_running_app()
        
        # Get the current date based on the active view
        if self.current_view == 'month':
            current_date = self.month_view.current_date
        elif self.current_view == 'week':
            current_date = self.week_view.current_date
        else:  # day
            current_date = self.day_view.current_date
            
        app.show_pdf_preview(self.current_view, current_date)
