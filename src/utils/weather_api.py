"""
Weather API integration to get weather forecasts.
"""
import requests
from datetime import datetime, timedelta
import json
import os

class WeatherAPI:
    """Weather API client for fetching forecasts."""
    
    def __init__(self, api_key=None, location=None):
        self.api_key = api_key
        self.location = location
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        self.cache_file = os.path.join(self.cache_dir, "weather_cache.json")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Initialize cache
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load the weather cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save the weather cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except IOError as e:
            print(f"Error saving weather cache: {e}")
    
    def get_forecast(self, date):
        """
        Get weather forecast for the specified date.
        
        Args:
            date (datetime): Date to get forecast for
            
        Returns:
            dict: Weather forecast data
        """
        if not self.api_key or not self.location:
            return None
        
        # Check cache first
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.cache:
            cached_data = self.cache[date_str]
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            
            # Use cache if it's less than 6 hours old
            if datetime.now() - cache_time < timedelta(hours=6):
                return cached_data['data']
        
        # If we need a forecast for a date more than 7 days in the future,
        # we can't get accurate data, so return a placeholder
        if date - datetime.now() > timedelta(days=7):
            return {
                'temperature': None,
                'condition': 'Forecast unavailable',
                'icon': None
            }
        
        # For this example, we'll use OpenWeatherMap API
        # You would need to sign up for a free API key
        api_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': self.location,
            'appid': self.api_key,
            'units': 'metric'  # or 'imperial' for Fahrenheit
        }
        
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Find the forecast closest to the requested date
            forecasts = data['list']
            target_forecast = None
            
            for forecast in forecasts:
                forecast_time = datetime.fromtimestamp(forecast['dt'])
                if forecast_time.date() == date.date():
                    # Pick a forecast from the middle of the day if possible
                    if forecast_time.hour in [9, 10, 11, 12, 13, 14, 15]:
                        target_forecast = forecast
                        break
                    # Otherwise just use the first one we find for that day
                    elif not target_forecast:
                        target_forecast = forecast
            
            if target_forecast:
                result = {
                    'temperature': target_forecast['main']['temp'],
                    'condition': target_forecast['weather'][0]['description'],
                    'icon': target_forecast['weather'][0]['icon']
                }
                
                # Cache the result
                self.cache[date_str] = {
                    'timestamp': datetime.now().isoformat(),
                    'data': result
                }
                self._save_cache()
                
                return result
            
            return None
        
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def get_week_forecast(self, start_date):
        """
        Get weather forecast for a week starting from the specified date.
        
        Args:
            start_date (datetime): Start date for the week
            
        Returns:
            list: List of daily forecasts
        """
        forecasts = []
        current_date = start_date
        
        for _ in range(7):
            forecast = self.get_forecast(current_date)
            forecasts.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'forecast': forecast
            })
            current_date += timedelta(days=1)
        
        return forecasts
