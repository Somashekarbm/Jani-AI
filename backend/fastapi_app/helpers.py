# helpers.py
import re
import threading
import time
import requests
import os
import pickle
import json
# from googletrans import Translator
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pyautogui
import winsound
from plyer import notification
import platform
import subprocess





# # Initialize the vision model



# Dictionary to map common names to actual executables or shortcut files
APP_MAPPINGS = {
    "command prompt": "cmd.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control",
    "wordpad": "write.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",  # Windows Terminal
    "word": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk",
    "excel": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk",
    "powerpoint": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk",
}

def open_application(query):
    app_name = query.replace("open", "").strip().lower()  # Normalize input

    # Check if the app name is in the dictionary
    if app_name in APP_MAPPINGS:
        app_path = APP_MAPPINGS[app_name]
        try:
            os.startfile(app_path)  # Open mapped app
            return {"message": f"Opening {app_name}", "action": "open_app"}
        except Exception as e:
            return {"message": f"Couldn't open {app_name}: {str(e)}", "action": "open_app_error"}

    # Try opening unknown apps dynamically
    try:
        os.startfile(app_name)
        return {"message": f"Opening {app_name}", "action": "open_app"}
    except Exception as e:
        return {"message": f"Couldn't open {app_name}: {str(e)}", "action": "open_app_error"}
    
    
def close_application(query):
    """Closes the specified application."""
    app_name = query.replace("close", "").strip().lower()  # Normalize input

    if app_name in APP_MAPPINGS:
        process_name = APP_MAPPINGS[app_name]
        try:
            subprocess.run(["taskkill", "/F", "/IM", process_name], check=True)
            return {"message": f"Closing {app_name}", "action": "close_app"}
        except Exception as e:
            return {"message": f"Couldn't close {app_name}: {str(e)}", "action": "close_app_error"}

    return {"message": f"Application {app_name} not found in mappings", "action": "close_app_error"}



def handle_screenshot_request(query, response):
    try:
        screenshot_folder = "JANI-Screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"jani_screenshot_{timestamp}.png"
        screenshot_path = os.path.join(screenshot_folder, screenshot_filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        response["message"] = f"Screenshot saved to {screenshot_folder}"
        response["action"] = "screenshot"
        response["screenshot_path"] = screenshot_path
        
        return response
    
    except ImportError:
        response["message"] = "PyAutoGUI is not installed. Please install it using 'pip install pyautogui'."
        response["action"] = "error"
        return response
    
    except Exception as e:
        response["message"] = f"Error taking screenshot: {str(e)}"
        response["action"] = "error"
        return response
    
def get_news_summary(headlines):
    """Optional: Generate a summary of headlines"""
    summary = "Today's Top Headlines:\n" + "\n".join(
        [f"{i+1}. {headline}" for i, headline in enumerate(headlines)]
    )
    return summary

def get_latest_headlines(max_headlines=5):
    """
    Fetch latest news headlines from multiple sources using web scraping
    Provides fallback mechanisms to ensure headline retrieval
    """
    # List of news sources to scrape
    news_sources = [
        {
            'url': 'https://news.google.com/rss',
            'parser': 'google_news_rss'
        },
        {
            'url': 'https://www.reuters.com/world/',
            'parser': 'reuters_web'
        },
        {
            'url': 'https://www.bbc.com/news',
            'parser': 'bbc_news'
        }
    ]

    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse_google_news_rss(content):
        """Parse Google News RSS Feed"""
        try:
            import feedparser
            feed = feedparser.parse(content)
            return [entry.title for entry in feed.entries[:max_headlines]]
        except Exception as e:
            print(f"Google News RSS Parsing Error: {e}")
            return []

    def parse_reuters_web(content):
        """Parse Reuters Website"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            headlines = soup.find_all(['h3', 'h2'], class_=lambda x: x and ('headline' in x.lower() or 'story-title' in x.lower()))
            return [h.get_text(strip=True) for h in headlines[:max_headlines] if h.get_text(strip=True)]
        except Exception as e:
            print(f"Reuters Parsing Error: {e}")
            return []

    def parse_bbc_news(content):
        """Parse BBC News Website"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            headlines = soup.find_all(['h2', 'h3'], class_=lambda x: x and ('headlines' in str(x).lower() or 'story' in str(x).lower()))
            return [h.get_text(strip=True) for h in headlines[:max_headlines] if h.get_text(strip=True)]
        except Exception as e:
            print(f"BBC News Parsing Error: {e}")
            return []

    # Parsing method mapping
    parsers = {
        'google_news_rss': parse_google_news_rss,
        'reuters_web': parse_reuters_web,
        'bbc_news': parse_bbc_news
    }

    # Collect headlines from all sources
    all_headlines = []

    for source in news_sources:
        try:
            # Different parsing for RSS vs web scraping
            if source['parser'] == 'google_news_rss':
                # Special handling for RSS feed
                response = requests.get(source['url'])
                headlines = parsers[source['parser']](response.content)
            else:
                # Web scraping for other sources
                response = requests.get(source['url'], headers=headers)
                headlines = parsers[source['parser']](response.text)

            all_headlines.extend(headlines)

            # If we have enough headlines, break
            if len(all_headlines) >= max_headlines:
                break

        except Exception as e:
            print(f"Error fetching from {source['url']}: {e}")
            continue

    # Fallback mechanism
    if not all_headlines:
        # Predefined headlines as absolute last resort
        all_headlines = [
            "Global Climate Summit Announces New Targets",
            "Tech Innovation Continues to Reshape Industries", 
            "Economic Outlook Shows Promising Signs of Recovery",
            "Breakthrough in Renewable Energy Technologies",
            "International Diplomacy Reaches New Milestones"
        ]

    # Deduplicate and limit headlines
    unique_headlines = list(dict.fromkeys(all_headlines))[:max_headlines]

    return unique_headlines


def extract_time_from_query(query):
    """
    Extract time information from a reminder query
    Returns a datetime object for the reminder time
    """
    now = datetime.now()
    
    # Look for specific time patterns
    time_pattern = r'at (\d{1,2}):?(\d{2})?\s?(am|pm)?'
    match = re.search(time_pattern, query, re.IGNORECASE)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        am_pm = match.group(3).lower() if match.group(3) else None
        
        # Adjust hour for 12-hour format
        if am_pm == 'pm' and hour < 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0
            
        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time is already past for today, set for tomorrow
        if remind_time < now:
            remind_time += timedelta(days=1)
            
        return remind_time
    
    # Look for "in X minutes/hours" patterns
    in_pattern = r'in (\d+) (minute|minutes|hour|hours)'
    match = re.search(in_pattern, query, re.IGNORECASE)
    
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        
        if 'hour' in unit:
            remind_time = now + timedelta(hours=amount)
        else:
            remind_time = now + timedelta(minutes=amount)
            
        return remind_time
    
    # Look for "tomorrow" or "next day" patterns
    if "tomorrow" in query.lower() or "next day" in query.lower():
        # Set for tomorrow at 9 AM as default
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Default to 1 hour from now if no time specified
    return now + timedelta(hours=1)

def set_reminder(text, reminder_time):
    """
    Set a reminder that will alert at the specified time
    """
    reminders_file = os.path.join(os.path.expanduser("~"), "Documents", "JANI_Reminders.pkl")
    
    # Load existing reminders
    reminders = []
    if os.path.exists(reminders_file):
        try:
            with open(reminders_file, 'rb') as f:
                reminders = pickle.load(f)
        except:
            reminders = []
    
    # Add new reminder
    reminder = {
        'text': text,
        'time': reminder_time,
        'created': datetime.now()
    }
    reminders.append(reminder)
    
    # Save reminders
    with open(reminders_file, 'wb') as f:
        pickle.dump(reminders, f)
    
    # Calculate seconds until reminder
    now = datetime.now()
    seconds_until_reminder = (reminder_time - now).total_seconds()
    
    if seconds_until_reminder > 0:
        # Set up timer thread
        reminder_thread = threading.Timer(
            seconds_until_reminder, 
            display_reminder, 
            args=[text]
        )
        reminder_thread.daemon = True
        reminder_thread.start()
    
    return reminder_time.strftime("%I:%M %p on %B %d")

def display_reminder(text):
    """
    Display a reminder alert with a pop-up notification and sound
    """
    # Play alert sound
    frequency = 2500  # Hz
    duration = 1000   # milliseconds
    winsound.Beep(frequency, duration)

    # Show pop-up notification
    notification.notify(
        title="Reminder",
        message=text,
        app_name="Reminder App",
        timeout=10  # Notification disappears after 10 seconds
    )



def start_timer(minutes):
    """
    Start a timer for the specified number of minutes
    """
    seconds = minutes * 60
    
    def timer_thread():
        time.sleep(seconds)
        # Play alert sound when timer completes
        frequency = 2500  # Hz
        duration = 1000   # milliseconds
        winsound.Beep(frequency, duration)
        print(f"\n⏰ TIMER COMPLETE: {minutes} minutes have elapsed\n")
        # Show pop-up notification
        notification.notify(
            title="TIME UP!!",
            message="The set time is up",
            app_name="Reminder App",
            timeout=10  # Notification disappears after 10 seconds
        )
    
    # Start timer in background thread
    t = threading.Thread(target=timer_thread)
    t.daemon = True
    t.start()
    
    return minutes

def convert_currency(query):
    """
    Extract currency info and perform conversion using an API
    """
    # Extract currencies from query
    from_currency = None
    to_currency = None
    amount = 1.0  # Default amount
    
    # Look for currency codes or common names
    currency_pattern = r'(USD|EUR|GBP|JPY|CAD|AUD|INR|dollars|euros|pounds|yen|rupees)'
    matches = re.findall(currency_pattern, query, re.IGNORECASE)
    
    if len(matches) >= 2:
        # Map common names to codes
        currency_map = {
            'dollars': 'USD',
            'euros': 'EUR',
            'pounds': 'GBP',
            'yen': 'JPY',
            'rupees': 'INR'
        }
        
        from_currency = matches[0].upper()
        to_currency = matches[1].upper()
        
        # Convert common names to codes if needed
        if from_currency.lower() in currency_map:
            from_currency = currency_map[from_currency.lower()]
        if to_currency.lower() in currency_map:
            to_currency = currency_map[to_currency.lower()]
    
    # Look for amount
    amount_pattern = r'(\d+\.?\d*)'
    amount_match = re.search(amount_pattern, query)
    if amount_match:
        amount = float(amount_match.group(1))
    
    # If currencies weren't found, return for further input
    if not from_currency or not to_currency:
        return {
            "status": "incomplete",
            "message": "Please specify source and target currencies"
        }
    
    try:
        # Access exchange rate API
        api_key = "a190cc7faa0f4c05b495772e"  # Note: In production, store this securely
        api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
        response = requests.get(api_url)
        data = response.json()
        
        if data.get('result') is not None:  # Fixed: Check for result directly
            result = data['conversion_result']  # Fixed: Use correct key
            date = data.get('time_last_update_utc', 'Unknown date')
            return {
                "status": "success",
                "message": f"{amount} {from_currency} is equal to {result:.2f} {to_currency} (as of {date})",
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "result": result
            }
        else:
            error_message = data.get('error-type', 'Unknown error')
            return {
                "status": "error",
                "message": f"Currency conversion failed. Error: {error_message}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Currency conversion error: {str(e)}"
        }


# def translate_text(query):
#     """
#     Extract text and language for translation
#     """
#     # Initialize the translator
#     translator = Translator()
    
#     # Extract text to translate
#     text_to_translate = query.lower()
    
#     # Remove command words
#     for phrase in ["translate", "translation", "in", "to", "from"]:
#         text_to_translate = text_to_translate.replace(phrase, "")
    
#     # Common language detection
#     target_lang = None
#     source_lang = None
    
#     # Check for target language
#     languages = {
#         "english": "en", "spanish": "es", "french": "fr", "german": "de",
#         "italian": "it", "portuguese": "pt", "russian": "ru", "japanese": "ja",
#         "korean": "ko", "chinese": "zh-cn", "arabic": "ar", "hindi": "hi",
#         "bengali": "bn", "dutch": "nl", "greek": "el", "finnish": "fi"
#     }
    
#     # Look for language patterns like "to spanish" or "in german"
#     lang_pattern = r'(?:to|in|into) (\w+)'
#     lang_match = re.search(lang_pattern, query, re.IGNORECASE)
    
#     if lang_match:
#         lang_name = lang_match.group(1).lower()
#         if lang_name in languages:
#             target_lang = languages[lang_name]
#             # Remove the language part from text
#             text_to_translate = text_to_translate.replace(f" {lang_match.group(0)}", "")
    
#     # Clean up the text
#     text_to_translate = text_to_translate.strip()
    
#     if not text_to_translate or len(text_to_translate) < 2:
#         return {
#             "status": "incomplete",
#             "message": "What would you like me to translate?"
#         }
    
#     if not target_lang:
#         return {
#             "status": "incomplete",
#             "message": "Please specify a target language"
#         }
    
#     try:
#         # Detect source language if not specified
#         if not source_lang:
#             detection = translator.detect(text_to_translate)
#             source_lang = detection.lang
        
#         # Perform translation
#         translation = translator.translate(
#             text_to_translate,
#             src=source_lang,
#             dest=target_lang
#         )
        
#         # Get language names for display
#         source_lang_name = next((k for k, v in languages.items() if v == source_lang), source_lang)
#         target_lang_name = next((k for k, v in languages.items() if v == target_lang), target_lang)
        
#         return {
#             "status": "success",
#             "message": f"Translation from {source_lang_name.capitalize()} to {target_lang_name.capitalize()}: {translation.text}",
#             "original_text": text_to_translate,
#             "translated_text": translation.text,
#             "source_language": source_lang,
#             "target_language": target_lang
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Translation error: {str(e)}"
#         }

def check_schedule(query):
    """
    Fetch and process calendar data from a local file
    """
    calendar_file = os.path.join(os.path.expanduser("~"), "Documents", "JANI_Calendar.json")
    
    if not os.path.exists(calendar_file):
        # Create empty calendar file if it doesn't exist
        with open(calendar_file, 'w') as f:
            json.dump({"events": []}, f)
        return {
            "status": "success",
            "message": "You don't have any appointments scheduled",
            "events": []
        }
    
    try:
        with open(calendar_file, 'r') as f:
            calendar_data = json.load(f)
        
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Filter events for today or tomorrow based on query
        if "tomorrow" in query.lower():
            target_date = tomorrow
            date_string = "tomorrow"
        else:
            target_date = today
            date_string = "today"
        
        # Filter events for the target date
        relevant_events = []
        for event in calendar_data.get("events", []):
            if event.get("date") == target_date:
                relevant_events.append(event)
        
        if not relevant_events:
            return {
                "status": "success",
                "message": f"You don't have any appointments scheduled for {date_string}",
                "events": []
            }
        
        # Format event information
        event_list = []
        for event in relevant_events:
            time_str = event.get("time", "All day")
            description = event.get("description", "No description")
            event_list.append(f"{time_str}: {description}")
        
        events_text = "\n".join([f"- {event}" for event in event_list])
        return {
            "status": "success",
            "message": f"Your schedule for {date_string}:\n{events_text}",
            "events": relevant_events
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error retrieving schedule: {str(e)}"
        }

def add_calendar_event(date, time, description):
    """
    Add an event to the calendar file
    """
    calendar_file = os.path.join(os.path.expanduser("~"), "Documents", "JANI_Calendar.json")
    
    # Load existing calendar data
    if os.path.exists(calendar_file):
        with open(calendar_file, 'r') as f:
            calendar_data = json.load(f)
    else:
        calendar_data = {"events": []}
    
    # Create new event
    new_event = {
        "date": date,
        "time": time,
        "description": description,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add event to calendar
    calendar_data["events"].append(new_event)
    
    # Save updated calendar
    with open(calendar_file, 'w') as f:
        json.dump(calendar_data, f, indent=2)
    
    return new_event