"""
Calendar view implementation with month, week, and day views.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty
from datetime import datetime, timedelta
import calendar as cal

class MonthView(GridLayout):
    """Month calendar view."""
    
    current_date = ObjectProperty(datetime.now())
    
    def __init__(self, **kwargs):
        super(MonthView, self).__init__(**kwargs)
        self.cols = 7  # 7 days in a week
        self.bind(current_date=self.update_month)
        self.update_month()
    
    def update_month(self, *args):
        """Update the month view based on the current date."""
        self.clear_widgets()
        
        # Add day of week headers
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            self.add_widget(Label(text=day))
        
        # Get the calendar for the current month
        calendar = cal.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Add the days to the grid
        for week in calendar:
            for day in week:
                if day == 0:
                    # Add an empty cell for days not in the current month
                    self.add_widget(Label(text=""))
                else:
                    # Create a button for each day in the month
                    day_btn = Button(text=str(day))
                    day_btn.bind(on_press=lambda btn, d=day: self.day_selected(d))
                    self.add_widget(day_btn)
    
    def day_selected(self, day):
        """Called when a day is selected in the month view."""
        selected_date = datetime(self.current_date.year, self.current_date.month, day)
        # Dispatch a custom event that parent widgets can listen for
        self.parent.switch_to_day_view(selected_date)
    
    def next_month(self):
        """Move to the next month."""
        if self.current_date.month == 12:
            self.current_date = datetime(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month + 1, 1)
    
    def previous_month(self):
        """Move to the previous month."""
        if self.current_date.month == 1:
            self.current_date = datetime(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month - 1, 1)


class WeekView(GridLayout):
    """Week calendar view with weather information."""
    
    current_date = ObjectProperty(datetime.now())
    
    def __init__(self, **kwargs):
        super(WeekView, self).__init__(**kwargs)
        self.cols = 1
        self.bind(current_date=self.update_week)
        self.update_week()
    
    def update_week(self, *args):
        """Update the week view based on the current date."""
        self.clear_widgets()
        
        # Find the start of the week (Monday)
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        
        # Create a row for each day of the week
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
            
            # Day label
            day_name = day_date.strftime("%a")
            day_number = day_date.strftime("%d")
            day_label = Label(text=f"{day_name} {day_number}", size_hint_x=0.2)
            day_layout.add_widget(day_label)
            
            # Events container
            events_container = BoxLayout(orientation='vertical', size_hint_x=0.6)
            # Here you would add events from the calendar
            events_container.add_widget(Label(text="No events"))
            day_layout.add_widget(events_container)
            
            # Weather container
            weather_container = BoxLayout(orientation='vertical', size_hint_x=0.2)
            weather_container.add_widget(Label(text="Weather"))
            day_layout.add_widget(weather_container)
            
            self.add_widget(day_layout)
    
    def next_week(self):
        """Move to the next week."""
        self.current_date = self.current_date + timedelta(days=7)
    
    def previous_week(self):
        """Move to the previous week."""
        self.current_date = self.current_date - timedelta(days=7)


class DayView(ScrollView):
    """Day calendar view with checklist interface."""
    
    current_date = ObjectProperty(datetime.now())
    
    def __init__(self, **kwargs):
        super(DayView, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.bind(current_date=self.update_day)
        self.update_day()
    
    def update_day(self, *args):
        """Update the day view based on the current date."""
        self.layout.clear_widgets()
        
        # Display date header
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        self.layout.add_widget(Label(text=date_str, size_hint_y=None, height=50))
        
        # Display weather information
        weather_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        weather_layout.add_widget(Label(text="Weather:"))
        # Here you would fetch and display weather information
        weather_layout.add_widget(Label(text="Fetching..."))
        self.layout.add_widget(weather_layout)
        
        # Display calendar events
        self.layout.add_widget(Label(text="Events", size_hint_y=None, height=40))
        # Here you would add events from the calendar
        
        # Add checklist section
        self.layout.add_widget(Label(text="Tasks", size_hint_y=None, height=40))
        self.add_checklist_item("Morning routine")
        self.add_checklist_item("Check emails")
        self.add_checklist_item("Project meeting")
        self.add_checklist_item("Workout")
        
        # Add button for adding new checklist items
        add_btn = Button(text="Add Task", size_hint_y=None, height=50)
        add_btn.bind(on_press=self.add_new_task)
        self.layout.add_widget(add_btn)
    
    def add_checklist_item(self, task_text):
        """Add a checklist item to the day view."""
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        checkbox = CheckBox(size_hint_x=0.1)
        label = Label(text=task_text, size_hint_x=0.9, halign='left')
        label.bind(size=label.setter('text_size'))
        item.add_widget(checkbox)
        item.add_widget(label)
        self.layout.add_widget(item)
        return item
    
    def add_new_task(self, instance):
        """Add a new empty task to the checklist."""
        self.add_checklist_item("New task")
    
    def next_day(self):
        """Move to the next day."""
        self.current_date = self.current_date + timedelta(days=1)
    
    def previous_day(self):
        """Move to the previous day."""
        self.current_date = self.current_date - timedelta(days=1)


class CalendarView(BoxLayout):
    """Main calendar view container with navigation between different views."""
    
    current_view = StringProperty("month")
    current_date = ObjectProperty(datetime.now())
    
    def __init__(self, **kwargs):
        super(CalendarView, self).__init__(**kwargs)
        self.orientation = "vertical"
        
        # Create navigation buttons
        nav_layout = BoxLayout(size_hint_y=0.1)
        self.prev_btn = Button(text="Previous")
        self.prev_btn.bind(on_press=self.previous)
        
        self.view_btn = Button(text="Month View")
        self.view_btn.bind(on_press=self.toggle_view)
        
        self.next_btn = Button(text="Next")
        self.next_btn.bind(on_press=self.next)
        
        nav_layout.add_widget(self.prev_btn)
        nav_layout.add_widget(self.view_btn)
        nav_layout.add_widget(self.next_btn)
        
        self.add_widget(nav_layout)
        
        # Content area
        self.content_area = BoxLayout(size_hint_y=0.9)
        self.add_widget(self.content_area)
        
        # Create the different views
        self.month_view = MonthView()
        self.week_view = WeekView()
        self.day_view = DayView()
        
        # Initially show month view
        self.show_month_view()
    
    def show_month_view(self):
        """Switch to month view."""
        self.content_area.clear_widgets()
        self.content_area.add_widget(self.month_view)
        self.current_view = "month"
        self.view_btn.text = "Month View"
        self.month_view.current_date = self.current_date
    
    def show_week_view(self):
        """Switch to week view."""
        self.content_area.clear_widgets()
        self.content_area.add_widget(self.week_view)
        self.current_view = "week"
        self.view_btn.text = "Week View"
        self.week_view.current_date = self.current_date
    
    def show_day_view(self):
        """Switch to day view."""
        self.content_area.clear_widgets()
        self.content_area.add_widget(self.day_view)
        self.current_view = "day"
        self.view_btn.text = "Day View"
        self.day_view.current_date = self.current_date
    
    def switch_to_day_view(self, date):
        """Switch to day view for the specified date."""
        self.current_date = date
        self.show_day_view()
    
    def toggle_view(self, instance):
        """Toggle between month, week, and day views."""
        if self.current_view == "month":
            self.show_week_view()
        elif self.current_view == "week":
            self.show_day_view()
        else:
            self.show_month_view()
    
    def next(self, instance):
        """Move to the next time period based on current view."""
        if self.current_view == "month":
            self.month_view.next_month()
        elif self.current_view == "week":
            self.week_view.next_week()
        else:
            self.day_view.next_day()
    
    def previous(self, instance):
        """Move to the previous time period based on current view."""
        if self.current_view == "month":
            self.month_view.previous_month()
        elif self.current_view == "week":
            self.week_view.previous_week()
        else:
            self.day_view.previous_day()
