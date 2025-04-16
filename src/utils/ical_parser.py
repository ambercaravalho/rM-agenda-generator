"""
iCalendar parser to extract calendar events.
"""
from datetime import datetime, timedelta
import requests
from icalendar import Calendar
from dateutil.rrule import rrulestr
from dateutil.parser import parse as parse_date

class ICalParser:
    """Parser for iCalendar files."""
    
    def __init__(self, ical_url=None):
        self.ical_url = ical_url
        self.calendar = None
    
    def set_ical_url(self, url):
        """Set the iCalendar URL."""
        self.ical_url = url
        self.calendar = None
    
    def fetch_calendar(self):
        """Fetch the calendar data from the URL."""
        if not self.ical_url:
            return False
        
        try:
            response = requests.get(self.ical_url)
            response.raise_for_status()
            self.calendar = Calendar.from_ical(response.text)
            return True
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching calendar: {e}")
            return False
    
    def get_events(self, start_date, end_date):
        """
        Get events within the specified date range.
        
        Args:
            start_date (datetime): Start date for event range
            end_date (datetime): End date for event range
            
        Returns:
            list: List of event dictionaries
        """
        if not self.calendar:
            if not self.fetch_calendar():
                return []
        
        events = []
        for component in self.calendar.walk():
            if component.name != "VEVENT":
                continue
            
            event = {
                'summary': str(component.get('summary', 'No Title')),
                'description': str(component.get('description', '')),
                'location': str(component.get('location', '')),
                'all_day': False
            }
            
            # Handle start and end times
            dtstart = component.get('dtstart')
            if dtstart:
                event['start'] = dtstart.dt
                # Check if it's an all-day event
                if not isinstance(event['start'], datetime):
                    event['all_day'] = True
                    # Convert date to datetime for consistency
                    event['start'] = datetime.combine(event['start'], datetime.min.time())
            else:
                continue  # Skip events with no start time
            
            dtend = component.get('dtend')
            if dtend:
                event['end'] = dtend.dt
                if not isinstance(event['end'], datetime) and event['all_day']:
                    event['end'] = datetime.combine(event['end'], datetime.min.time())
            else:
                event['end'] = event['start'] + timedelta(hours=1)
            
            # Handle recurring events
            rrule = component.get('rrule')
            if rrule:
                # Generate recurrences in the date range
                rule_text = f"RRULE:{rrule.to_ical().decode('utf-8')}"
                rule = rrulestr(rule_text, dtstart=event['start'])
                
                for recurrence_date in rule.between(start_date, end_date):
                    recurring_event = event.copy()
                    duration = recurring_event['end'] - recurring_event['start']
                    recurring_event['start'] = recurrence_date
                    recurring_event['end'] = recurrence_date + duration
                    events.append(recurring_event)
            else:
                # Check if one-time event is in range
                if start_date <= event['start'] <= end_date or start_date <= event['end'] <= end_date:
                    events.append(event)
        
        return events
