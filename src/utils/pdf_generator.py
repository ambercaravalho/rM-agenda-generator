"""
PDF generator for creating calendar PDFs for reMarkable tablets.
"""
import os
import calendar
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from kivy.app import App

class PDFGenerator:
    """PDF Generator for reMarkable calendar layouts."""
    
    def __init__(self):
        # Register fonts
        self._register_fonts()
        
        # Get the tablet model from the app
        app = App.get_running_app()
        self.tablet_model = app.tablet_model if hasattr(app, 'tablet_model') else "reMarkable 2"
        
        # Set page size and capabilities based on tablet model
        self.page_size, self.supports_color = self._get_tablet_specs()
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=1  # Center
        ))
        self.styles.add(ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=10
        ))
        self.styles.add(ParagraphStyle(
            name='Small',
            fontName='Helvetica',
            fontSize=8
        ))
        self.styles.add(ParagraphStyle(
            name='Heading2',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6
        ))
    
    def _get_tablet_specs(self):
        """
        Get page size and color capabilities based on tablet model.
        
        Returns:
            tuple: (page_size, supports_color)
        """
        # Default to reMarkable 2 specs if model is None
        if not self.tablet_model:
            self.tablet_model = "reMarkable 2"
            
        if self.tablet_model == "reMarkable 1":
            # reMarkable 1: 1872×1404 pixels (226 DPI)
            # Close to A5 in portrait orientation, monochrome
            return portrait((595, 842)), False
            
        elif self.tablet_model == "reMarkable 2":
            # reMarkable 2: 1872×1404 pixels (226 DPI) 
            # Similar to A5 in portrait orientation, monochrome
            return portrait((595, 842)), False
            
        elif self.tablet_model == "Paper Pro":
            # reMarkable Paper Pro (assumed specs similar to reMarkable 2 but with color)
            # Portrait orientation, with color support
            return portrait((595, 842)), True
            
        else:
            # Default to reMarkable 2 specs
            return portrait((595, 842)), False
    
    def _register_fonts(self):
        """Register custom fonts for PDF generation."""
        # You can add custom fonts here if needed
        pass
    
    def generate_month_calendar(self, year, month, output_path, events=None, include_weather=False):
        """
        Generate a monthly calendar PDF.
        
        Args:
            year (int): Year for the calendar
            month (int): Month for the calendar
            output_path (str): Directory to save the PDF
            events (dict, optional): Calendar events to include
            include_weather (bool, optional): Whether to include weather information
            
        Returns:
            str: Path to the generated PDF file
        """
        filename = os.path.join(output_path, f"monthly_calendar_{year}_{month:02d}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=self.page_size, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        
        # Title
        month_name = calendar.month_name[month]
        title = Paragraph(f"{month_name} {year}", self.styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Get the calendar data
        cal = calendar.monthcalendar(year, month)
        
        # Day names header
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        cal_data = [day_names]
        
        # Add the days to the calendar
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    # Empty cell for days not in this month
                    week_data.append("")
                else:
                    day_text = str(day)
                    if events:
                        # Add events for this day if available
                        day_events = self._get_events_for_day(events, year, month, day)
                        if day_events:
                            day_text += "\n" + "\n".join(day_events)
                    week_data.append(day_text)
            cal_data.append(week_data)
        
        # Create the calendar table with adjusted cell width based on tablet model
        col_width = (self.page_size[0] - 60) / 7  # Distribute available width among 7 columns
        table = Table(cal_data, colWidths=[col_width] * 7, rowHeights=[30] + [80] * len(cal))
        
        # Style the table
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        # Add colors if the tablet supports it
        if self.supports_color:
            table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightblue)
            table_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue)
        else:
            table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            table_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.black)
        
        table_style.add('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10)
        table_style.add('FONT', (0, 1), (-1, -1), 'Helvetica', 9)
        
        table.setStyle(table_style)
        
        elements.append(table)
        doc.build(elements)
        
        return filename

    def generate_week_calendar(self, start_date, output_path, events=None, weather=None):
        """
        Generate a weekly calendar PDF.
        
        Args:
            start_date (datetime): Start date for the week
            output_path (str): Directory to save the PDF
            events (dict, optional): Calendar events to include
            weather (dict, optional): Weather forecast data
            
        Returns:
            str: Path to the generated PDF file
        """
        # Format the filename with the week's start and end dates
        end_date = start_date + timedelta(days=6)
        filename = os.path.join(
            output_path, 
            f"weekly_calendar_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.pdf"
        )
        
        doc = SimpleDocTemplate(filename, pagesize=self.page_size, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        
        # Title
        title = Paragraph(
            f"Week of {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}", 
            self.styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Create a table for the week
        table_data = []
        
        # Headers
        headers = ["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        table_data.append(headers)
        
        # Calculate cell widths based on the tablet page size
        available_width = self.page_size[0] - 60  # account for margins
        time_col_width = 40
        day_col_width = (available_width - time_col_width) / 7
        
        # Add date row
        current_date = start_date
        date_row = ["Date"]
        for _ in range(7):
            date_str = current_date.strftime("%d/%m")
            
            # Add weather if available and tablet supports color
            if weather and current_date.strftime("%Y-%m-%d") in weather:
                w = weather[current_date.strftime("%Y-%m-%d")]
                if w:
                    weather_text = f"\n{w['condition']}\n{w['temperature']}°C"
                    date_str += weather_text
            
            date_row.append(date_str)
            current_date += timedelta(days=1)
        
        table_data.append(date_row)
        
        # Add time slots
        for hour in range(8, 21):  # 8 AM to 8 PM
            hour_str = f"{hour:02d}:00"
            row = [hour_str]
            
            # Add empty cells for each day
            current_date = start_date
            for day in range(7):
                # Check if there are events at this time
                event_text = ""
                if events:
                    date_key = current_date.strftime("%Y-%m-%d")
                    if date_key in events:
                        for event in events[date_key]:
                            event_hour = event['start'].hour
                            if event_hour == hour:
                                event_text += f"{event['summary']}\n"
                row.append(event_text)
                current_date += timedelta(days=1)
            
            table_data.append(row)
        
        # Create the table with adjusted widths based on tablet model
        table = Table(
            table_data, 
            colWidths=[time_col_width] + [day_col_width] * 7, 
            rowHeights=[30, 50] + [25] * (len(table_data) - 2)
        )
        
        # Style the table
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
            ('VALIGN', (0, 2), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        # Apply colors if the tablet supports them
        if self.supports_color:
            table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightblue)
            table_style.add('BACKGROUND', (0, 1), (-1, 1), colors.lightblue)
            table_style.add('BACKGROUND', (0, 1), (0, -1), colors.lightblue)
            table_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue)
        else:
            table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            table_style.add('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey)
            table_style.add('BACKGROUND', (0, 1), (0, -1), colors.lightgrey)
            table_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.black)
        
        table_style.add('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10)
        table_style.add('FONT', (0, 1), (0, -1), 'Helvetica-Bold', 9)
        table_style.add('FONT', (1, 1), (-1, -1), 'Helvetica', 8)
        
        table.setStyle(table_style)
        
        elements.append(table)
        doc.build(elements)
        
        return filename

    def generate_day_calendar(self, date, output_path, events=None, weather=None, tasks=None):
        """
        Generate a daily calendar PDF.
        
        Args:
            date (datetime): Date for the calendar
            output_path (str): Directory to save the PDF
            events (list, optional): Calendar events to include
            weather (dict, optional): Weather forecast data
            tasks (list, optional): Checklist tasks
            
        Returns:
            str: Path to the generated PDF file
        """
        filename = os.path.join(output_path, f"daily_calendar_{date.strftime('%Y%m%d')}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=self.page_size, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        
        # Title
        title = Paragraph(date.strftime("%A, %B %d, %Y"), self.styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Weather section
        if weather:
            weather_style = self.styles['Normal'].clone('WeatherStyle')
            if self.supports_color:
                weather_style.textColor = colors.darkblue
            
            weather_str = f"Weather: {weather['condition']}, {weather['temperature']}°C"
            weather_para = Paragraph(weather_str, weather_style)
            elements.append(weather_para)
            elements.append(Spacer(1, 15))
        
        # Schedule section
        elements.append(Paragraph("Schedule", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Create a table for hourly schedule
        schedule_data = [["Time", "Event"]]
        
        # Calculate cell widths based on the tablet page size
        available_width = self.page_size[0] - 60  # account for margins
        time_col_width = 60
        event_col_width = available_width - time_col_width
        
        # Add time slots for the day
        for hour in range(8, 21):  # 8 AM to 8 PM
            hour_str = f"{hour:02d}:00"
            event_text = ""
            
            # Check if there are events at this time
            if events:
                for event in events:
                    if event['start'].hour == hour:
                        event_text = event['summary']
                        if event.get('location'):
                            event_text += f" - {event['location']}"
                        break
            
            schedule_data.append([hour_str, event_text])
        
        schedule_table = Table(schedule_data, colWidths=[time_col_width, event_col_width])
        
        # Style the schedule table
        schedule_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        # Apply colors if the tablet supports them
        if self.supports_color:
            schedule_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightblue)
            schedule_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue)
        else:
            schedule_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            schedule_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.black)
        
        schedule_style.add('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10)
        schedule_style.add('FONT', (0, 1), (0, -1), 'Helvetica-Bold', 9)
        schedule_style.add('FONT', (1, 1), (1, -1), 'Helvetica', 10)
        
        schedule_table.setStyle(schedule_style)
        
        elements.append(schedule_table)
        elements.append(Spacer(1, 20))
        
        # Tasks section
        elements.append(Paragraph("Tasks", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Create a table for tasks with adjusted width based on tablet model
        task_col_width = available_width - 20  # checkbox column is 20 points
        
        if tasks and len(tasks) > 0:
            task_data = [["□", task] for task in tasks]
            task_table = Table(task_data, colWidths=[20, task_col_width])
            
            # Style the task table
            task_style = TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONT', (0, 0), (0, -1), 'Helvetica', 12),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10)
            ])
            task_table.setStyle(task_style)
            
            elements.append(task_table)
        else:
            # Empty task list with checkbox placeholders
            empty_tasks = [["□", ""] for _ in range(10)]
            empty_task_table = Table(empty_tasks, colWidths=[20, task_col_width], rowHeights=[25] * 10)
            
            # Style the empty task table
            empty_task_style = TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONT', (0, 0), (0, -1), 'Helvetica', 12)
            ])
            empty_task_table.setStyle(empty_task_style)
            
            elements.append(empty_task_table)
        
        # Notes section
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Notes", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Create a notes area with proper width for the tablet
        notes_data = [[""]]
        notes_table = Table(notes_data, colWidths=[available_width], rowHeights=[200])
        
        # Style the notes table
        notes_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        notes_table.setStyle(notes_style)
        
        elements.append(notes_table)
        doc.build(elements)
        
        return filename
        
    def _get_events_for_day(self, events, year, month, day):
        """Helper method to get events for a specific day."""
        date_key = f"{year:04d}-{month:02d}-{day:02d}"
        if date_key in events:
            return [e['summary'] for e in events[date_key]]
        return []

# Function to be called from external modules
def generate_calendar_pdf(view_type, output_path, date=None, events=None, weather=None, tasks=None):
    """
    Generate a calendar PDF based on the specified view type.
    
    Args:
        view_type (str): One of 'month', 'week', or 'day'
        output_path (str): Directory to save the PDF
        date (datetime, optional): Date for the calendar, defaults to today
        events (dict, optional): Calendar events to include
        weather (dict, optional): Weather forecast data
        tasks (list, optional): Checklist tasks for day view
        
    Returns:
        str: Path to the generated PDF file
    """
    if date is None:
        date = datetime.now()
    
    generator = PDFGenerator()
    
    if view_type == 'month':
        return generator.generate_month_calendar(date.year, date.month, output_path, events)
    elif view_type == 'week':
        # Find the start of the week (Monday)
        start_of_week = date - timedelta(days=date.weekday())
        return generator.generate_week_calendar(start_of_week, output_path, events, weather)
    elif view_type == 'day':
        return generator.generate_day_calendar(date, output_path, events, weather, tasks)
    else:
        raise ValueError(f"Invalid view type: {view_type}. Must be one of 'month', 'week', or 'day'")
