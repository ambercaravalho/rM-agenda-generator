"""
PDF generator for the reMarkable Agenda Generator.
"""
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from kivy.app import App

def generate_calendar_pdf(view_type, date, output_path, include_months=True, include_weeks=True, include_days=True):
    """
    Generate a calendar PDF with the specified view type and date.
    
    Args:
        view_type: The type of calendar view ('month', 'week', or 'day')
        date: The date to generate the calendar for
        output_path: The path to save the PDF to
        include_months: Whether to include monthly view (default: True)
        include_weeks: Whether to include weekly view (default: True)
        include_days: Whether to include daily view (default: True)
        
    Returns:
        The path to the generated PDF file
    """
    try:
        # Get dimensions from app configuration
        app = App.get_running_app()
        dimensions = app.get_dimensions()
        supports_color = app.supports_color
        
        # Create the PDF document
        c = canvas.Canvas(output_path, pagesize=(dimensions['width_pt'], dimensions['height_pt']))
        
        # Based on the selected components, generate multiple views
        # If no components are selected, default to the primary view type
        any_component_selected = include_months or include_weeks or include_days
        
        if not any_component_selected:
            if view_type == 'month':
                include_months = True
            elif view_type == 'week':
                include_weeks = True
            elif view_type == 'day':
                include_days = True
        
        # Generate requested views
        if include_months:
            _draw_month_view(c, date, supports_color, dimensions)
            if include_weeks or include_days:
                c.showPage()  # Start a new page
        
        if include_weeks:
            _draw_week_view(c, date, supports_color, dimensions)
            if include_days:
                c.showPage()  # Start a new page
        
        if include_days:
            _draw_day_view(c, date, supports_color, dimensions)
        
        c.save()
        return output_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Create a simple error PDF
        try:
            c = canvas.Canvas(output_path, pagesize=(595, 842))  # A4 size
            c.setFont("Helvetica", 14)
            c.drawString(100, 700, f"Error generating calendar: {str(e)}")
            c.save()
        except:
            pass
        return output_path

def _draw_month_view(c, date, supports_color, dimensions):
    """Draw a month view calendar."""
    try:
        width_pt = dimensions['width_pt']
        height_pt = dimensions['height_pt']
        
        # Basic page setup
        c.setFont("Helvetica", 24)
        
        # Set title color
        if supports_color:
            c.setFillColor(colors.blue)
        else:
            c.setFillColor(colors.black)
            
        # Draw the month and year at the top
        month_name = date.strftime("%B %Y")
        c.drawString(50, height_pt - 50, month_name)
        
        # Reset to black for the rest of the text
        c.setFillColor(colors.black)
        
        # Draw the calendar grid
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        # Draw the day names
        c.setFont("Helvetica", 12)
        x_start = 50
        y_start = height_pt - 100
        cell_width = (width_pt - 100) / 7
        
        for i, day in enumerate(days_of_week):
            c.drawString(x_start + i * cell_width + 10, y_start, day)
        
        # Draw horizontal line under day names
        c.line(x_start, y_start - 10, width_pt - 50, y_start - 10)
        
        # Calculate the first day of the month and the number of days
        first_day = date.replace(day=1)
        if first_day.month == 12:
            next_month = first_day.replace(year=first_day.year + 1, month=1, day=1)
        else:
            next_month = first_day.replace(month=first_day.month + 1, day=1)
        days_in_month = (next_month - first_day).days
        
        # Calculate the weekday of the first day (0 is Monday in Python's datetime)
        first_weekday = first_day.weekday()
        
        # Draw the days
        c.setFont("Helvetica", 14)
        y_pos = y_start - 40
        day_height = 80
        
        for i in range(days_in_month):
            day_num = i + 1
            col = (first_weekday + i) % 7
            row = (first_weekday + i) // 7
            
            x = x_start + col * cell_width + 10
            y = y_pos - row * day_height
            
            # Draw the day number
            c.drawString(x, y, str(day_num))
            
            # Draw a small box for the day
            c.rect(x - 5, y - 60, cell_width - 10, 65, stroke=1, fill=0)
    except Exception as e:
        print(f"Error drawing month view: {e}")
        c.drawString(50, height_pt - 100, f"Error drawing month view: {str(e)}")

def _draw_week_view(c, date, supports_color, dimensions):
    """Draw a week view calendar."""
    try:
        width_pt = dimensions['width_pt']
        height_pt = dimensions['height_pt']
        
        # Basic page setup
        c.setFont("Helvetica", 24)
        
        # Set title color
        if supports_color:
            c.setFillColor(colors.blue)
        else:
            c.setFillColor(colors.black)
        
        # Calculate start and end of week
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Draw the week date range at the top
        week_title = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
        c.drawString(50, height_pt - 50, week_title)
        
        # Reset to black for the rest of the text
        c.setFillColor(colors.black)
        
        # Draw the week grid
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Calculate grid dimensions
        y_start = height_pt - 100
        grid_height = height_pt - 150
        time_column_width = 60
        
        # Draw day headers
        c.setFont("Helvetica", 12)
        day_width = (width_pt - 50 - time_column_width) / 7
        
        for i, day in enumerate(days_of_week):
            current_date = start_of_week + timedelta(days=i)
            day_str = f"{day}\n{current_date.strftime('%d')}"
            
            # Center day name in column
            x_pos = 50 + time_column_width + (i * day_width) + (day_width / 2) - 20
            c.drawString(x_pos, y_start, day_str)
        
        # Draw vertical lines for days
        for i in range(8):
            x = 50 + time_column_width + (i * day_width)
            c.line(x, y_start - 20, x, height_pt - grid_height - 50)
        
        # Draw hourly rows
        c.setFont("Helvetica", 10)
        hour_height = (grid_height - 50) / 12  # Show 8am to 8pm (12 hours)
        
        for i in range(13):  # 13 lines for 12 hour slots
            hour = i + 8  # Start at 8am
            y_line = y_start - 20 - (i * hour_height)
            
            # Draw hour label
            hour_label = f"{hour}:00"
            if hour > 12:
                hour_label = f"{hour-12}:00 PM"
            elif hour == 12:
                hour_label = "12:00 PM"
            else:
                hour_label = f"{hour}:00 AM"
                
            c.drawString(55, y_line - 5, hour_label)
            
            # Draw horizontal line
            c.line(50 + time_column_width, y_line, width_pt - 50, y_line)
    except Exception as e:
        print(f"Error drawing week view: {e}")
        c.drawString(50, height_pt - 100, f"Error drawing week view: {str(e)}")

def _draw_day_view(c, date, supports_color, dimensions):
    """Draw a day view calendar."""
    try:
        width_pt = dimensions['width_pt']
        height_pt = dimensions['height_pt']
        
        # Basic page setup
        c.setFont("Helvetica", 24)
        
        # Set title color
        if supports_color:
            c.setFillColor(colors.blue)
        else:
            c.setFillColor(colors.black)
        
        # Draw the day at the top
        day_title = date.strftime("%A, %B %d, %Y")
        c.drawString(50, height_pt - 50, day_title)
        
        # Reset to black for the rest of the text
        c.setFillColor(colors.black)
        
        # Draw the day schedule
        y_start = height_pt - 100
        schedule_height = height_pt - 150
        
        # Draw hourly rows
        c.setFont("Helvetica", 12)
        hour_height = 40
        hours = min(24, int(schedule_height / hour_height))  # As many hours as will fit
        
        for i in range(hours + 1):  # +1 for the line at the bottom of the last hour
            hour = i
            y_line = y_start - (i * hour_height)
            
            # Draw hour label
            if hour < 24:  # Only draw labels for valid hours
                if hour == 0:
                    hour_label = "12:00 AM"
                elif hour < 12:
                    hour_label = f"{hour}:00 AM"
                elif hour == 12:
                    hour_label = "12:00 PM"
                else:
                    hour_label = f"{hour-12}:00 PM"
                    
                c.drawString(50, y_line - 15, hour_label)
            
            # Draw horizontal line
            c.line(150, y_line, width_pt - 50, y_line)
        
        # Draw a vertical line to separate the time from the schedule
        c.line(150, y_start, 150, y_start - (hours * hour_height))
    except Exception as e:
        print(f"Error drawing day view: {e}")
        c.drawString(50, height_pt - 100, f"Error drawing day view: {str(e)}")
