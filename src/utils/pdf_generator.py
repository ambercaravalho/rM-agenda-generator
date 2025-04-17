"""
PDF generator for the reMarkable Agenda Generator.
Creates calendar PDFs optimized for reMarkable tablets.
"""
import os
import calendar
import tempfile
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing
from PIL import Image, ImageDraw, ImageFont
import io

def generate_calendar_pdf(view_type, date, output_path, for_preview=False):
    """
    Generate a calendar PDF with the specified view type for the given date.
    
    Args:
        view_type (str): 'month', 'week', or 'day'
        date (datetime): Date to use for the calendar
        output_path (str): Path to save the PDF
        for_preview (bool): If True, generates a PDF optimized for preview
    """
    # Create the PDF with A5 size (reMarkable tablet dimensions)
    dimensions = (1404, 1872)  # reMarkable default dimensions (portrait)
    c = canvas.Canvas(output_path, pagesize=dimensions)
    
    # Set some defaults
    supports_color = False  # reMarkable tablets are typically grayscale
    
    # Draw header
    c.setFont("Helvetica-Bold", 24)
    if view_type == 'month':
        title = f"{date.strftime('%B %Y')}"
        _draw_month_view(c, date, supports_color, dimensions)
    elif view_type == 'week':
        # Find the first day of the week (Monday) for the given date
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        title = f"Week of {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
        _draw_week_view(c, date, supports_color, dimensions)
    elif view_type == 'day':
        title = f"{date.strftime('%A, %B %d, %Y')}"
        _draw_day_view(c, date, supports_color, dimensions)
    else:
        title = "Calendar"
    
    # Draw the title at the top of the page
    c.drawString(100, dimensions[1] - 100, title)
    
    # Save the PDF
    c.save()
    return output_path

def generate_preview_image(view_type, date, dpi=100):
    """
    Generate a preview image of the calendar using a cross-platform approach.
    
    Args:
        view_type (str): 'month', 'week', or 'day'
        date (datetime): Date to use for the calendar
        dpi (int): Resolution for the preview image
    
    Returns:
        str: Path to the generated preview image
    """
    # Create a temporary image file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
        temp_img_path = tmp_img.name
    
    try:
        # Use direct drawing approach for cross-platform compatibility
        # Calculate dimensions similar to reportlab (but scaled down for preview)
        scale_factor = 0.33  # Scale down for preview
        width, height = int(1404 * scale_factor), int(1872 * scale_factor)
        
        # Create a blank white image
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fall back to default if not available
        try:
            # Try to use a system font
            font_title = ImageFont.truetype("Arial", 24)
            font_regular = ImageFont.truetype("Arial", 12)
            font_bold = ImageFont.truetype("Arial Bold", 14)
        except:
            # Fall back to default font
            font_title = ImageFont.load_default()
            font_regular = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        # Draw title
        if view_type == 'month':
            title = f"{date.strftime('%B %Y')}"
            draw.text((30, 30), title, fill='black', font=font_title)
            _draw_month_view_image(draw, date, width, height, font_regular, font_bold)
        elif view_type == 'week':
            start_of_week = date - timedelta(days=date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            title = f"Week of {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
            draw.text((30, 30), title, fill='black', font=font_title)
            _draw_week_view_image(draw, date, width, height, font_regular, font_bold)
        elif view_type == 'day':
            title = f"{date.strftime('%A, %B %d, %Y')}"
            draw.text((30, 30), title, fill='black', font=font_title)
            _draw_day_view_image(draw, date, width, height, font_regular, font_bold)
        
        # Save the image
        image.save(temp_img_path)
        print(f"Preview image generated successfully: {temp_img_path}")
        
    except Exception as e:
        print(f"Error generating preview image: {e}")
        return None
    
    return temp_img_path

def _draw_month_view_image(draw, date, width, height, font_regular, font_bold):
    """Draw a month view calendar on a PIL Image."""
    # Get calendar for the current month
    cal = calendar.monthcalendar(date.year, date.month)
    
    # Define grid parameters
    margin = 20
    grid_top = 70
    cell_width = (width - 2 * margin) / 7
    cell_height = 40
    
    # Draw weekday headers
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        x = margin + i * cell_width
        draw.text((x + 5, grid_top), day, fill='black', font=font_bold)
    
    # Draw the grid
    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            if day > 0:
                x = margin + day_idx * cell_width
                y = grid_top + 20 + (week_idx * cell_height)
                
                # Draw cell border
                draw.rectangle(
                    [(x, y), (x + cell_width, y + cell_height)],
                    outline='black'
                )
                
                # Draw day number
                day_str = str(day)
                draw.text((x + 5, y + 5), day_str, fill='black', font=font_regular)
                
                # Highlight current day
                if date.day == day:
                    # Draw a circle around the current day
                    circle_x = x + 10
                    circle_y = y + 10
                    circle_radius = 10
                    draw.ellipse(
                        [(circle_x - circle_radius, circle_y - circle_radius),
                         (circle_x + circle_radius, circle_y + circle_radius)],
                        fill='lightgray',
                        outline='black'
                    )
                    # Redraw the text
                    draw.text((x + 5, y + 5), day_str, fill='black', font=font_regular)

def _draw_week_view_image(draw, date, width, height, font_regular, font_bold):
    """Draw a week view calendar on a PIL Image."""
    # Find the first day of the week (Monday)
    start_date = date - timedelta(days=date.weekday())
    
    # Define grid parameters
    margin = 20
    grid_top = 70
    day_height = 40
    
    # Draw each day of the week
    for day_idx in range(7):
        current_date = start_date + timedelta(days=day_idx)
        day_name = current_date.strftime("%A")
        day_date = current_date.strftime("%b %d")
        
        y = grid_top + (day_idx * day_height)
        
        # Draw day header
        day_text = f"{day_name}, {day_date}"
        draw.text((margin, y), day_text, fill='black', font=font_bold)
        
        # Draw horizontal line for this day
        draw.line([(margin, y + 20), (width - margin, y + 20)], fill='black')
        
        # Highlight current day
        if current_date.date() == date.date():
            # Draw rectangle behind the day text
            text_width = len(day_text) * 8  # Approximate width
            draw.rectangle(
                [(margin - 5, y - 5), (margin + text_width, y + 15)],
                fill='lightgray',
                outline=None
            )
            # Redraw the text
            draw.text((margin, y), day_text, fill='black', font=font_bold)

def _draw_day_view_image(draw, date, width, height, font_regular, font_bold):
    """Draw a day view calendar on a PIL Image."""
    # Define grid parameters
    margin = 20
    grid_top = 70
    hour_height = 25
    
    # Format the date nicely
    formatted_date = date.strftime("%A, %B %d, %Y")
    draw.text((margin, grid_top), formatted_date, fill='black', font=font_bold)
    
    # Draw hourly schedule (9 AM to 9 PM)
    for hour in range(9, 22):
        y = grid_top + 25 + ((hour - 9) * hour_height)
        
        # Draw hour label
        meridian = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
            
        time_text = f"{display_hour} {meridian}"
        draw.text((margin, y), time_text, fill='black', font=font_bold)
        
        # Draw hour line
        draw.line([(margin + 30, y), (width - margin, y)], fill='black')
        
        # Draw half-hour line (lighter)
        draw.line(
            [(margin + 30, y + (hour_height / 2)), (width - margin, y + (hour_height / 2))],
            fill='gray'
        )
    
    # Add a notes section at the bottom
    notes_y = grid_top + (14 * hour_height)
    draw.text((margin, notes_y), "Notes:", fill='black', font=font_bold)
    draw.line([(margin, notes_y + 15), (width - margin, notes_y + 15)], fill='black')

def _draw_month_view(c, date, supports_color, dimensions):
    """Draw a month view calendar."""
    # Get calendar for the current month
    cal = calendar.monthcalendar(date.year, date.month)
    
    # Define grid parameters
    width, height = dimensions
    margin = 50
    grid_top = height - 150
    cell_width = (width - 2 * margin) / 7
    cell_height = 100
    
    # Draw weekday headers
    c.setFont("Helvetica-Bold", 12)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        x = margin + i * cell_width
        c.drawString(x + 10, grid_top - 20, day)
    
    # Draw the grid
    c.setFont("Helvetica", 12)
    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            if day > 0:
                x = margin + day_idx * cell_width
                y = grid_top - (week_idx + 1) * cell_height
                
                # Draw cell border
                c.rect(x, y, cell_width, cell_height)
                
                # Draw day number
                c.drawString(x + 10, y + cell_height - 20, str(day))
                
                # Highlight current day
                if date.day == day:
                    c.setFillColor(colors.lightgrey)
                    c.circle(x + 20, y + cell_height - 15, 12, fill=1)
                    c.setFillColor(colors.black)
                    c.drawString(x + 10, y + cell_height - 20, str(day))

def _draw_week_view(c, date, supports_color, dimensions):
    """Draw a week view calendar."""
    # Find the first day of the week (Monday)
    start_date = date - timedelta(days=date.weekday())
    
    # Define grid parameters
    width, height = dimensions
    margin = 50
    grid_top = height - 150
    
    # Draw each day of the week
    c.setFont("Helvetica", 12)
    for day_idx in range(7):
        current_date = start_date + timedelta(days=day_idx)
        day_name = current_date.strftime("%A")
        day_date = current_date.strftime("%b %d")
        
        y = grid_top - day_idx * 100
        
        # Draw day header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, f"{day_name}, {day_date}")
        c.setFont("Helvetica", 12)
        
        # Draw horizontal line for this day
        c.line(margin, y - 10, width - margin, y - 10)
        
        # Highlight current day
        if current_date.date() == date.date():
            c.setFillColor(colors.lightgrey)
            c.rect(margin - 10, y - 5, width - 2*margin + 20, 25, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, y, f"{day_name}, {day_date}")
            c.setFont("Helvetica", 12)

def _draw_day_view(c, date, supports_color, dimensions):
    """Draw a day view calendar."""
    # Define grid parameters
    width, height = dimensions
    margin = 50
    grid_top = height - 150
    hour_height = 60
    
    # Format the date nicely
    formatted_date = date.strftime("%A, %B %d, %Y")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, grid_top + 20, formatted_date)
    
    # Draw hourly schedule (9 AM to 9 PM)
    for hour in range(9, 22):
        y = grid_top - (hour - 8) * hour_height
        
        # Draw hour label
        meridian = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"{display_hour} {meridian}")
        
        # Draw hour line
        c.line(margin + 60, y, width - margin, y)
        
        # Draw half-hour line (lighter)
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.grey)
        c.line(margin + 60, y - hour_height/2, width - margin, y - hour_height/2)
        c.setLineWidth(1)
        c.setStrokeColor(colors.black)
    
    # Add a notes section at the bottom
    notes_y = grid_top - 14 * hour_height
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, notes_y, "Notes:")
    c.line(margin, notes_y - 10, width - margin, notes_y - 10)
