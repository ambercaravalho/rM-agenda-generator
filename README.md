# reMarkable Agenda Generator

## Overview
This project is a Kivy-based desktop application designed to generate calendar PDFs optimized for reMarkable paper tablets. It supports multiple calendar views, weather integration, and task management.

## Features
- Calendar generation with month, week, and day views
- iCalendar integration to import events from external calendars
- Weather information integration for the current week
- Task checklist interface for daily planning
- PDF generation for reMarkable tablets
- Cross-platform support (Windows, macOS, and Linux)

## Project Structure
```
rM-agenda-generator
├── src
│   ├── main.py              # Entry point of the application
│   ├── app.py               # Main application class
│   ├── remarkable_api.py    # reMarkable Cloud API integration
│   ├── views
│   │   ├── calendar_view.py    # Calendar UI components
│   │   ├── settings_view.py    # Settings UI
│   │   └── pdf_preview_view.py # PDF preview UI
│   ├── utils
│   │   ├── ical_parser.py     # iCalendar parser
│   │   ├── weather_api.py     # Weather API integration
│   │   └── pdf_generator.py   # PDF generation utilities
│   └── cache                  # Directory for cached data
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Installation

### Pre-built Packages (Coming Soon)
Pre-built packages for Windows, macOS, and Linux will be available for download in the future. Once available, you'll be able to download and install them directly without needing to build from source.

### Building from Source

#### Prerequisites
- Python 3.7+ installed on your system

#### Setting up a Virtual Environment (Recommended)
1. Clone this repository:
   ```
   git clone https://github.com/ambercaravalho/rM-agenda-generator.git
   cd rM-agenda-generator
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application
To run the application, navigate to the `src` directory and execute the `main.py` file:
```
cd src
python main.py
```

## Usage
1. **Calendar Navigation**: Use the calendar views to navigate through month, week, and day displays.
2. **Import iCalendar**: In settings, add URLs for iCalendar subscriptions.
3. **Weather Integration**: Add your location and weather API key in settings.
4. **Task Management**: Use the day view to manage daily tasks with a checklist.
5. **PDF Generation**: Generate PDFs optimized for reMarkable tablets.

## reMarkable Integration
Note: The reMarkable Cloud API integration is currently a placeholder. Full integration requires additional development and may be subject to reMarkable's API availability and terms of service.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.