active_browsers = {
    "google": None,
    "youtube": None,
    "wikipedia": None
}


def initialize_browser_if_needed(browser_type):
    """Initialize browser if not already running"""
    if active_browsers[browser_type] is None:
        driver = webdriver.Chrome()  # Or Firefox, Edge, etc.
        active_browsers[browser_type] = driver
    return active_browsers[browser_type]

def control_active_browser(command):
    """Handle browser control commands"""
    # Find the active browser
    active_browser = None
    for browser in active_browsers.values():
        if browser is not None:
            active_browser = browser
            break
    
    if active_browser is None:
        return {"status": "error", "message": "No active browser to control"}
    
    # Process common browser commands
    if "scroll down" in command:
        active_browser.execute_script("window.scrollBy(0, 300)")
        return {"status": "success", "message": "Scrolled down", "action": "scroll_down"}
    
    elif "scroll up" in command:
        active_browser.execute_script("window.scrollBy(0, -300)")
        return {"status": "success", "message": "Scrolled up", "action": "scroll_up"}
    
    elif "go back" in command:
        active_browser.back()
        return {"status": "success", "message": "Navigated back", "action": "browser_back"}
    
    elif "refresh" in command or "reload" in command:
        active_browser.refresh()
        return {"status": "success", "message": "Page refreshed", "action": "browser_refresh"}
    
    # YouTube specific commands
    elif "play video" in command and "youtube" in active_browser.current_url:
        # Click the first video or the play button
        try:
            play_button = active_browser.find_element_by_css_selector("button.ytp-play-button")
            play_button.click()
            return {"status": "success", "message": "Playing video", "action": "youtube_play"}
        except:
            return {"status": "error", "message": "Couldn't play video", "action": "youtube_play_error"}
    
    elif "pause video" in command and "youtube" in active_browser.current_url:
        try:
            pause_button = active_browser.find_element_by_css_selector("button.ytp-play-button")
            pause_button.click()
            return {"status": "success", "message": "Paused video", "action": "youtube_pause"}
        except:
            return {"status": "error", "message": "Couldn't pause video", "action": "youtube_pause_error"}
    
    # Add more browser control commands as needed
    
    return {"status": "error", "message": "Unrecognized browser command", "action": "browser_unknown_command"}

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

def process_voice_command(query, is_follow_up=False):
    """
    Process voice commands with follow-up capability
    """
    query = query.lower()
    response = {
        "status": "success",
        "message": "",
        "action": "default"
    }
    
    # Check if this is a browser control command
    browser_control_commands = ["scroll down", "scroll up", "go back", "refresh", 
                              "play video", "pause video", "volume up", "volume down"]
    
    if any(cmd in query for cmd in browser_control_commands):
        return control_active_browser(query)
    
    # Process regular commands
    try:
        # YouTube Operations
        if 'open youtube' in query:
            try:
                browser = initialize_browser_if_needed("youtube")
                browser.get("https://www.youtube.com")
                response["message"] = "YouTube opened successfully"
                response["action"] = "open_youtube"
            except Exception as e:
                # Reset the browser instance if there was an error
                active_browsers["youtube"] = None
                browser = initialize_browser_if_needed("youtube")
                browser.get("https://www.youtube.com")
                response["message"] = "YouTube opened successfully after reconnecting"
                response["action"] = "open_youtube_reconnect"

        elif 'search youtube' in query:
            try:
                browser = initialize_browser_if_needed("youtube")
                if not "youtube.com" in browser.current_url:
                    browser.get("https://www.youtube.com")
                
                search_term = query.replace("search youtube for", "").replace("search youtube", "").strip()
                search_box = browser.find_element_by_name("search_query")
                search_box.clear()
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.RETURN)
                
                response["message"] = f"Searching YouTube for {search_term}"
                response["action"] = "youtube_search"
            except Exception as e:
                # Reset and try again
                active_browsers["youtube"] = None
                response["message"] = "Couldn't search YouTube. Please try again."
                response["action"] = "youtube_search_error"

        # Google Operations
        elif 'open google' in query:
            try:
                browser = initialize_browser_if_needed("google")
                browser.get("https://www.google.com")
                response["message"] = "Google opened successfully"
                response["action"] = "open_google"
            except Exception as e:
                # Reset the browser instance if there was an error
                active_browsers["google"] = None
                browser = initialize_browser_if_needed("google")
                browser.get("https://www.google.com")
                response["message"] = "Google opened successfully after reconnecting"
                response["action"] = "open_google_reconnect"
                
                
                @app.post("/voice_command")
async def voice_command(request: VoiceCommandRequest):
    """Asynchronous voice command endpoint with thread pool execution"""
    try:
        # Use thread pool to process command without blocking
        future = executor.submit(process_voice_command, request.command, request.is_follow_up)
        result = future.result(timeout=10)  # 10-second timeout
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Command processing failed: {str(e)}",
            "action": "error_handling"
        }



# 1. Remove or disable the Porcupine wake word detection since we're using the frontend
use_porcupine = False  # Set to False to disable backend wake word detection

# 2. Keep the wake_word_command endpoint for handling commands after frontend wake word detection
@app.post("/wake_word_command")
async def wake_word_command(request: VoiceCommandRequest):
    """Special endpoint for handling commands after wake word detection"""
    try:
        # Process the command from the frontend
        result = process_voice_command(request.command, is_follow_up=True)
        
        # Text-to-speech the response
        if result and "message" in result:
            speech_queue.speak(result["message"])
            
        return result
    except Exception as e:
        error_msg = f"Error processing wake word command: {str(e)}"
        speech_queue.speak("Sorry, I encountered an error")
        return {
            "status": "error",
            "message": error_msg,
            "action": "wake_word_command_error"
        }

# 3. Modify the main block to skip wake word setup
if __name__ == "__main__":
    try:
        # Skip Porcupine initialization
        if use_porcupine:  # This will now be False
            porcupine = setup_wake_word_detection()
        
        # Start the FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        # Clean up
        speech_queue.stop()
    except Exception as e:
        print(f"Startup error: {e}")
        speech_queue.stop()