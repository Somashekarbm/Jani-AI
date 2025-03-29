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
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor

# Pydantic model for voice command request
class VoiceCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=200)

app = FastAPI()

# Enable CORS for frontend
origins = ["http://localhost:5173"]

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

def handle_screenshot_request(query, response):
    try:
        screenshot_folder = "JANI-Screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
            response["message"] = "YouTube opened successfully"
            response["action"] = "open_youtube"

        elif 'search youtube' in query:
            search_term = query.replace("search youtube for", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}")
            response["message"] = f"Searching YouTube for {search_term}"
            response["action"] = "youtube_search"

        # Google Operations
        elif 'open google' in query:
            webbrowser.open("https://www.google.com")
            response["message"] = "Google opened successfully"
            response["action"] = "open_google"

        elif 'search google' in query:
            search_term = query.replace("search google for", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            response["message"] = f"Searching Google for {search_term}"
            response["action"] = "google_search"

        # Time
        elif 'the time' in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response["message"] = f"Sir, the time is {current_time}"
            response["action"] = "get_time"

        # Jokes
        elif 'joke' in query:
            joke = pyjokes.get_joke()
            response["message"] = joke
            response["action"] = "tell_joke"

        # Screenshot
        elif 'take a screenshot' in query:
            response = handle_screenshot_request(query, {})

        # Music
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
            

        # Weather (needs valid API key)
        elif "weather" in query:
            api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with actual key
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            
            # Simulate city input (in real implementation, you'd need voice input)
            city_name = "London"  # Default city
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            
            try:
                response_weather = requests.get(complete_url)
                x = response_weather.json()
                
                if x["cod"] != "404":
                    y = x["main"]
                    current_temperature = y["temp"]
                    current_pressure = y["pressure"]
                    current_humidity = y["humidity"]
                    z = x["weather"]
                    weather_description = z[0]["description"]
                    
                    weather_info = f"Temperature: {current_temperature} Kelvin, Pressure: {current_pressure} hPa, Humidity: {current_humidity}%, Description: {weather_description}"
                    response["message"] = weather_info
                    response["action"] = "weather_info"
                else:
                    response["message"] = "City Not Found"
                    response["action"] = "weather_error"
            except Exception as e:
                response["message"] = f"Weather fetch error: {str(e)}"
                response["action"] = "weather_error"

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

        # Personalized Interactions
        elif "who made you" in query or "who created you" in query:
            response["message"] = "I have been created by Somashekar."
            response["action"] = "creator_info"

        elif "who are you" in query:
            response["message"] = "I am your virtual assistant named as JANI, created by Somashekar"
            response["action"] = "self_intro"

        # Exit
        elif 'exit' in query:
            response["message"] = "Thanks for giving me your time"
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
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        speech_queue.stop()