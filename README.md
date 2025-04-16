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

### Prerequisites
- Ensure you have Python 3.7+ installed on your system.

### Installing Dependencies
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/rM-agenda-generator.git
   cd rM-agenda-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Installing Kivy on macOS
1. Open your terminal.
2. Ensure you have Homebrew installed. If not, install it from [brew.sh](https://brew.sh/).
3. Run the following command to install Kivy:
   ```
   brew install kivy
   ```
4. After installation, you can verify it by running the application.

### Installing Kivy on Windows
1. Open Command Prompt or PowerShell.
2. Run the following command:
   ```
   pip install kivy
   ```

### Installing Kivy on Linux
1. Open your terminal.
2. Run the following commands:
   ```
   pip install kivy
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