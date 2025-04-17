#VoiceCommand.py
import subprocess
import queue
import pyttsx3
import threading
import datetime
import wikipedia
import requests
from bs4 import BeautifulSoup
import random
import webbrowser
import os
import time
import winshell
import pyjokes
import pyautogui
import requests
import ctypes
import tempfile
import uvicorn
from PIL import Image
import base64
import torch
from io import BytesIO
from fastapi import FastAPI, HTTPException, APIRouter, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import speech_recognition as sr


# Import the helper functions
from helpers import (
    extract_time_from_query,
    set_reminder,
    start_timer,
    convert_currency,
    check_schedule,
    add_calendar_event,
    handle_screenshot_request,
    get_latest_headlines,
    get_news_summary,
    open_application,
    close_application,
    
)

# Pydantic model for voice command request
class VoiceCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=200)

    
app = FastAPI()

    
# Enable CORS for frontend
origins = ["http://localhost:5173","http://localhost:5174"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#handling the speech functionality on the frontend itself using api
#speechqueue impl
class SpeechQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton implementation to ensure only one instance exists"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize all necessary components"""
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.engine = None
        self._initialize_engine()
        
        # Start the speech worker thread
        self.thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.thread.start()

    def _initialize_engine(self):
        """Initialize the TTS engine with robust settings"""
        try:
            # Ensure previous engine is stopped
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass

            # Create new engine
            self.engine = pyttsx3.init('sapi5')
            voices = self.engine.getProperty('voices')
            
            # Use first available voice
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Set speech properties
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            print("TTS Engine Reinitialized Successfully")
        except Exception as e:
            print(f"TTS Engine Initialization Error: {e}")
            self.engine = None

    def _speech_worker(self):
        """Background thread to process speech queue"""
        while not self.stop_event.is_set():
            try:
                # Use get with a timeout to check stop_event periodically
                text = self.queue.get(timeout=0.5)
                
                if text is None:
                    break
                
                if self.engine:
                    try:
                        print(f"Speaking: {text}")
                        # Reset the engine before speaking
                        self.engine.stop()
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as speak_error:
                        print(f"Speech Attempt Error: {speak_error}")
                        # Reinitialize engine on speaking error
                        self._initialize_engine()
                
                # Mark task as done
                self.queue.task_done()
            except queue.Empty:
                # No item in queue, just continue checking
                continue
            except Exception as e:
                print(f"Speech Worker Error: {e}")
                # Prevent tight error loop
                time.sleep(0.5)
                self._initialize_engine()

    def speak(self, text):
        """Add text to speech queue with deduplication"""
        if text and not self.queue.full():
            self.queue.put(text)

    def stop(self):
        """Stop speech and terminate thread"""
        self.stop_event.set()
        self.queue.put(None)
        if hasattr(self, 'thread'):
            self.thread.join()

    def __del__(self):
        """Ensure cleanup on object deletion"""
        self.stop()

# Global speech queue
speech_queue = SpeechQueue()

# Thread pool for handling concurrent tasks
executor = ThreadPoolExecutor(max_workers=3)





def process_voice_command(query):
    """
    Centralized command processing with comprehensive functionality
    Returns a response dictionary for frontend communication
    """
    query = query.lower()
    response = {
        "status": "success",
        "message": "",
        "action": "default"
    }

    try:
        # Wikipedia Search
        if 'wikipedia' in query:
            try:
                search_query = query.replace("wikipedia", "").strip()
                results = wikipedia.summary(search_query, sentences=3)
                response["message"] = results
                response["action"] = "wikipedia_search"
            except Exception as e:
                response["status"] = "error"
                response["message"] = f"Wikipedia search failed: {str(e)}"

        # YouTube Operations
        elif 'open youtube' in query:
            webbrowser.open("https://www.youtube.com")
            response["message"] = "Boss, YouTube opened successfully"
            response["action"] = "open_youtube"

        elif 'search youtube' in query:
            search_term = query.replace("search youtube for", "").replace("search youtube", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}")
            response["message"] = f"Searching YouTube for {search_term}"
            response["action"] = "youtube_search"

        # Google Operations
        elif 'open google' in query:
            webbrowser.open("https://www.google.com")
            response["message"] = "Boss, Google opened successfully"
            response["action"] = "open_google"

        #"search google for leetcode {any problem name}"
        elif 'search google' in query:
            search_term = query.replace("search google for", "").replace("search google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            response["message"] = f"Searching Google for {search_term}"
            response["action"] = "google_search"
            
            
        # Reminder functionality "remind me in 1/2 minutes to check email" #works
        elif "remind me" in query:
            reminder_text = query.replace("remind me", "").strip()
            
            # Extract pattern like "remind me to call mom at 5pm"
            # or "remind me in 30 minutes to check email"
            reminder_time = extract_time_from_query(query)
            
            # Set up the reminder
            formatted_time = set_reminder(reminder_text, reminder_time)
            
            response["message"] = f"Ok Boss, I'll remind you: {reminder_text} at {formatted_time}"
            response["action"] = "set_reminder"
        
        # Currency conversion  #-- try "convert currency 1 rupees to dollars"
        elif "convert currency" in query or "exchange rate" in query:
            # First check if we have all needed info
            result = convert_currency(query)
            
            if result["status"] == "incomplete":
                # Need more information
                response["message"] = result["message"]
                response["action"] = "currency_conversion_request"
            elif result["status"] == "error":
                # Error occurred
                response["status"] = "error"
                response["message"] = result["message"]
                response["action"] = "currency_conversion_error"
            else:
                # Successful conversion
                response["message"] = result["message"]
                response["action"] = "currency_conversion_result"
            
        # Time
        elif 'the time' in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response["message"] = f"Boss, the time is {current_time}"
            response["action"] = "get_time"
            
        elif 'the date' in query or 'today\'s date' in query:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            response["message"] = f"Boss, Today's date is {current_date}"
            response["action"] = "get_date"
            
        elif "take a note" in query or "create a note" in query:
            notes_dir = os.path.join(os.path.expanduser("~"), "Documents", "JANI_Notes")
            os.makedirs(notes_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            note_file = os.path.join(notes_dir, f"note_{timestamp}.txt")
            
            # Get the content for the note
            note_content = query.replace("take a note", "").replace("create a note", "").strip()
            
            if not note_content:
                response["message"] = "Boss, What would you like me to note down?"
                response["action"] = "note_request_content"
            else:
                with open(note_file, "w") as f:
                    f.write(note_content)
                response["message"] = f"Boss, Note created and saved as note_{timestamp}.txt"
                response["action"] = "note_created"
                
        #just lists the notes name present in the documents folder
        elif "read my notes" in query or "list notes" in query:
            notes_dir = os.path.join(os.path.expanduser("~"), "Documents", "JANI_Notes")
            if os.path.exists(notes_dir):
                notes = os.listdir(notes_dir)
                if notes:
                    notes_list = "\n".join(notes)
                    response["message"] = f"Boss, Your notes are:\n{notes_list}"
                    response["action"] = "list_notes"
                else:
                    response["message"] = "Boss, You don't have any notes yet."
                    response["action"] = "no_notes"
            else:
                response["message"] = "Boss, Notes directory not found"
                response["action"] = "notes_error"
                
        # Schedule checking  #checks for schedule working
        elif "what's on my schedule" in query or "my appointments" in query or "my calendar" in query:
            # Get schedule data
            result = check_schedule(query)
            
            if result["status"] == "error":
                response["status"] = "error"
                response["message"] = result["message"]
                response["action"] = "schedule_error"
            else:
                response["message"] = result["message"]
                response["action"] = "check_schedule"
                response["events"] = result["events"]
                
        # Calendar events  default_time = "12:00 PM" sets some event to 12:00pm , just tell "add event event1"
        elif "add event" in query or "add to calendar" in query:
            # This is a simplified version - in reality, you'd likely use a calendar API
            event_details = query.replace("add event", "").replace("add to calendar", "").strip()
            
            # In a real implementation, you would parse the date and time
            # For now, we'll use today's date and a default time
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            default_time = "12:00 PM"
            
            # Add the event to the calendar
            add_calendar_event(today, default_time, event_details)
                
            response["message"] = f"Boss, Event added: {event_details}"
            response["action"] = "add_event"
                
        # Timer  #working try one minute  "set timer for one minute"
        elif "set timer" in query or "start timer" in query:
            # Extract time in minutes from query
            time_str = ''.join(c for c in query if c.isdigit())
            
            if time_str:
                minutes = int(time_str)
                # Start the timer in background
                start_timer(minutes)
                
                response["message"] = f"Boss, Timer set for {minutes} minutes"
                response["action"] = "set_timer"
            else:
                response["message"] = "Please specify a time for the timer"
                response["action"] = "timer_no_time"
                
        # Open applications  #works open notepad
        elif "open" in query or "open app" in query:
            response=open_application(query)
            
        #close the opened apps
        elif "close" in query or "close app" in query:
            response=close_application(query)
                
        elif "create folder" in query:   #working
            folder_name = query.replace("create folder", "").strip()
            os.makedirs(folder_name, exist_ok=True)
            response["message"] = f"Boss, Folder '{folder_name}' created Successfully!"
            response["action"] = "create_folder"

        # Jokes
        elif 'joke' in query:
            joke = pyjokes.get_joke()
            response["message"] = joke
            response["action"] = "tell_joke"

        # Screenshot
        elif 'take a screenshot' in query:
            response = handle_screenshot_request(query, {})
            
        elif "take selfie" in query or "take photo" in query:
            import cv2
            from datetime import datetime
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                # Capture frame
                ret, frame = cap.read()
                if ret:
                    # Save image
                    img_name = f"selfie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(img_name, frame)
                    response["message"] = f"Selfie taken and saved as {img_name}"
                else:
                    response["message"] = "Failed to capture image"
            else:
                response["message"] = "Camera not available"
            
            # Release camera
            cap.release()
            response["action"] = "take_selfie"

        # Music  #imp this
        elif 'play music' in query or "play song" in query:
            music_dir = r"C:\Users\Somu\Music"
            if os.path.exists(music_dir):
                songs = os.listdir(music_dir)
                if songs:
                    os.startfile(os.path.join(music_dir, songs[1]))
                    response["message"] = "Playing music"
                    response["action"] = "play_music"
                else:
                    response["message"] = "No songs found in the music directory"
                    response["action"] = "music_error"
            else:
                response["message"] = "Music directory not found"
                response["action"] = "music_error"

        # News
        elif "show news" in query or "today's news" in query or "headlines" in query:
            try:
                headlines = get_latest_headlines()
                response["message"] = get_news_summary(headlines)
                response["action"] = "show_news"
            except Exception as e:
                print(f"News fetching failed: {e}")
            
        # Weather
        elif "weather" in query:
            import requests
            import json
            
            api_key = "8ee685cd294a00e09aa8e067ce03e1d3"  # Your OpenWeatherMap API key
            
            try:
                # Step 1: Get the current location using IP geolocation
                # Using ipinfo.io which doesn't require an API key for basic usage
                ip_response = requests.get("https://ipinfo.io/json")
                ip_data = ip_response.json()
                
                # Extract location information
                location = ip_data.get("loc", "").split(",")
                city_name = ip_data.get("city", "Unknown")
                region = ip_data.get("region", "")
                country = ip_data.get("country", "")
                
                if len(location) != 2:
                    # If we couldn't get location coordinates, use fallback method
                    response["message"] = "Couldn't determine your location automatically. Using default location.\n"
                    # Use geocoding API as fallback
                    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
                    geo_response = requests.get(geocoding_url)
                    geo_data = geo_response.json()
                    
                    if not geo_data:
                        response["message"] = "Sorry, I couldn't determine your location. Please try again later."
                        response["action"] = "weather_error"
                        return response
                        
                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                else:
                    # Use coordinates from IP geolocation
                    lat = location[0]
                    lon = location[1]
                
                # Step 2: Use the free Current Weather API instead of OneCall API (which requires subscription)
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
                weather_response = requests.get(weather_url)
                weather_data = weather_response.json()
                
                # Check if we got a valid response
                if weather_data.get("cod") != 200:
                    error_message = weather_data.get("message", "Unknown API error")
                    response["message"] = f"Error from weather service: {error_message}"
                    response["action"] = "weather_error"
                    return response
                
                # Format the location display
                location_display = f"{city_name}, {region}, {country}" if region else f"{city_name}, {country}"
                
                # Extract weather information from the response
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                temp_min = weather_data['main']['temp_min']
                temp_max = weather_data['main']['temp_max']
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                weather_description = weather_data['weather'][0]['description']
                
                # Format the weather information
                weather_info = (
                    f"Weather in your current location ({location_display}):\n"
                    f"Currently: {weather_description.title()}\n"
                    f"Temperature: {temp}°C (Feels like: {feels_like}°C)\n"
                    f"Today's Range: {temp_min}°C to {temp_max}°C\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind Speed: {wind_speed} m/s"
                )
                
                response["message"] = weather_info
                response["action"] = "weather_info"
                    
            except Exception as e:
                response["message"] = f"Unable to fetch weather information: {str(e)}\nPlease check your internet connection and API key."
                response["action"] = "weather_error"
                
        elif "record audio" in query or "record voice" in query:
            import pyaudio
            import wave
            import threading
            
            # Extract duration if specified
            duration = 5  # Default 5 seconds
            digits = ''.join(c for c in query if c.isdigit())
            if digits:
                duration = int(digits)
            
            def record_audio(duration_sec, filename="recording.wav"):
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
                
                frames = []
                for i in range(0, int(RATE / CHUNK * duration_sec)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # Start recording
            filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            threading.Thread(target=record_audio, args=(duration, filename)).start()
            
            response["message"] = f"Recording audio for {duration} seconds. Saving to {filename}"
            response["action"] = "record_audio"

        elif "define" in query or "meaning of" in query:
            word = query.replace("define", "").replace("meaning of", "").strip()
            try:
                # Using PyDictionary or similar library
                from PyDictionary import PyDictionary
                dictionary = PyDictionary()
                meaning = dictionary.meaning(word)
                if meaning:
                    response["message"] = f"Definition of {word}: {meaning}"
                else:
                    response["message"] = f"Sorry, I couldn't find the meaning of {word}"
            except:
                response["message"] = "Sorry, dictionary service is unavailable"
            response["action"] = "dictionary_lookup"
        # System Commands
        elif 'lock window' in query:
            ctypes.windll.user32.LockWorkStation()
            response["message"] = "Locking the device"
            response["action"] = "lock_system"

        elif 'shutdown system' in query:
            subprocess.call('shutdown /p /f')
            response["message"] = "Shutting down system"
            response["action"] = "shutdown_system"

        elif 'restart' in query:
            subprocess.call(["shutdown", "/r"])
            response["message"] = "Restarting system"
            response["action"] = "restart_system"
            
        elif "system info" in query or "computer info" in query:
            import platform
            import psutil
            
            system_info = f"System: {platform.system()} {platform.version()}\n"
            system_info += f"Processor: {platform.processor()}\n"
            memory = psutil.virtual_memory()
            system_info += f"RAM: {memory.total / (1024**3):.2f} GB (Used: {memory.percent}%)\n"
            disk = psutil.disk_usage('/')
            system_info += f"Disk: {disk.total / (1024**3):.2f} GB (Used: {disk.percent}%)"
            
            response["message"] = system_info
            response["action"] = "system_info"
        
            
        # Volume control
        elif "volume up" in query:
            pyautogui.press("volumeup")
            response["message"] = "Increasing volume"
            response["action"] = "volume_up"
            
        elif "volume down" in query:
            pyautogui.press("volumedown")
            response["message"] = "Decreasing volume"
            response["action"] = "volume_down"
            
        elif "mute" in query:
            pyautogui.press("volumemute")
            response["message"] = "Muting/Unmuting audio"
            response["action"] = "volume_mute"
            
        elif "brightness" in query:
            import screen_brightness_control as sbc
            
            if "increase brightness" in query:
                current = sbc.get_brightness()[0]
                sbc.set_brightness(min(current + 10, 100))
                response["message"] = "Increased screen brightness"
            elif "decrease brightness" in query:
                current = sbc.get_brightness()[0]
                sbc.set_brightness(max(current - 10, 0))
                response["message"] = "Decreased screen brightness"
            elif "set brightness" in query:
                # Extract percentage
                percent = int(''.join(c for c in query if c.isdigit()))
                if 0 <= percent <= 100:
                    sbc.set_brightness(percent)
                    response["message"] = f"Set brightness to {percent}%"
                else:
                    response["message"] = "Please specify brightness between 0 and 100%"
            else:
                current = sbc.get_brightness()[0]
                response["message"] = f"Current brightness is {current}%"
            
            response["action"] = "brightness_control"

        # Personalized Interactions
        elif "who made you" in query or "who created you" in query:
            response["message"] = "I have been created by Somashekar and team."
            response["action"] = "creator_info"

        elif "who are you" in query:
            response["message"] = "I am your virtual assistant named as JANI, created by Somashekar and team."
            response["action"] = "self_intro"

        # Exit  #implement this later 
        elif 'exit' in query:
            response["message"] = "Thanks for using my services! Have a great day!"
            response["action"] = "exit_assistant"

        else:
            response["status"] = "unknown_command"
            response["message"] = "Command not recognized"
            response["action"] = "default"

    except Exception as e:
        response["status"] = "error"
        response["message"] = f"An unexpected error occurred: {str(e)}"
        response["action"] = "error_handling"

    return response



@app.post("/record_voice")
async def record_voice():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for voice input...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            
        print("Processing audio...")
        text = r.recognize_google(audio, language="en-IN")
        print(f"Recognized: {text}")
        return {"status": "success", "text": text}
    except sr.WaitTimeoutError:
        raise HTTPException(status_code=400, detail="Listening timed out")
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand audio")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not request results from speech service: {str(e)}")
    except Exception as e:
        print(f"Error in speech recognition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/voice_command")
async def voice_command(request: VoiceCommandRequest):
    """Asynchronous voice command endpoint with thread pool execution"""
    try:
        # Use thread pool to process command without blocking
        future = executor.submit(process_voice_command, request.command)
        result = future.result(timeout=10)  # 10-second timeout
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Command processing failed: {str(e)}",
            "action": "error_handling"
        }
        


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8010)
    except KeyboardInterrupt:
        speech_queue.stop()