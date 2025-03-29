import subprocess
import queue
# import wolframalpha
import pyttsx3
import tkinter
import json
import random
import operator
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime
import wikipedia
import webbrowser
import os
import winshell
import pyjokes
import pyautogui
import feedparser
import smtplib
import ctypes
import time
import requests
import shutil
# from twilio.rest import Client
# from clint.textui import progress
from ecapture import ecapture as ec
from bs4 import BeautifulSoup
import win32com.client as wincl
from urllib.request import urlopen
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



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


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


assiname = "Jaani 1 point o" 



# def speak(text):
#     """Speak text using pyttsx3 with manual event loop management."""
#     engine.say(text)
#     if not engine._inLoop:
#         engine.startLoop(False)
#         while engine.isBusy():
#             engine.iterate()
#         engine.endLoop()

def speak(text):
    """ Speak text without threading issues """
    engine.say(text)
    engine.runAndWait()  # Run normally to avoid threading issues




def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Sir !")
    elif 12 <= hour < 18:
        speak("Good Afternoon Sir !")
    else:
        speak("Good Evening Sir !")
    
    speak("I am your Assistant")
    speak(assiname)

# def username():
#     speak("What should I call you, sir?")
#     uname = takeCommand()
#     speak("Welcome Mister")
#     speak(uname)
#     columns = shutil.get_terminal_size().columns
    
#     print("#####################".center(columns))
#     print(f"Welcome Mr. {uname}".center(columns))
#     print("#####################".center(columns))
    
#     speak("How can I help you, Sir?")

# -----

# def takeCommand(callback=None):
#     """Non-blocking voice command function using threading"""
#     def listen_and_process():
#         recognizer = sr.Recognizer()
#         with sr.Microphone() as source:
#             print("Listening...")
#             recognizer.adjust_for_ambient_noise(source, duration=0.5)
#             try:
#                 audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
#                 print("Recognizing...")
#                 query = recognizer.recognize_google(audio, language='en-in')
#                 print(f"User said: {query}")
#                 if callback:
#                     callback(query.lower())  # Process the command in a separate function
#             except sr.UnknownValueError:
#                 print("Could not understand audio")
#                 if callback:
#                     callback("none")
#             except sr.RequestError:
#                 print("API unavailable")
#                 if callback:
#                     callback("none")
    
#     threading.Thread(target=listen_and_process, daemon=True).start()
    
    
def takeCommand(callback=None):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)  # Helps with background noise
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"User said: {command}")

                if callback:  # Call the callback function if provided
                    callback(command)
                return command
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand. Can you repeat?")
                if callback:
                    callback(None)
                return None
            except sr.RequestError:
                speak("Speech recognition service is unavailable right now.")
                if callback:
                    callback(None)
                return None




# def sendEmail(to, content):
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.ehlo()
#     server.starttls()
#     server.login('your email id', 'your email password')
#     server.sendmail('your email id', to, content)
#     server.close()

def openYouTube():
    """Opens YouTube in the browser"""
    speak("Opening YouTube")
    webbrowser.open("https://www.youtube.com")
    time.sleep(5)  # Give time for YouTube to load

def searchYouTube(query):
    """Searches YouTube using voice input"""
    speak(f"Searching for {query} on YouTube")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
    time.sleep(5)
    pyautogui.press('enter')

def focusYouTubeTab():
    """Brings the YouTube tab to focus if it's already open"""
    speak("Switching to YouTube tab")
    pyautogui.hotkey("ctrl", "1")
    
def searchYouTube(query):
    """Searches YouTube using the search bar in the same tab"""
    speak(f"Searching for {query} on YouTube")
    focusYouTubeTab()
    pyautogui.press("/")  # Shortcut to focus the search bar
    time.sleep(1)
    pyautogui.write(query)
    pyautogui.press("enter")
    
def controlYouTube(command):
    actions = {
        "pause": "space",
        "play": "space",
        "mute": "m",
        "unmute": "m",
        "volume up": "up",
        "volume down": "down",
        "next": "shift+n",
        "previous": "shift+p",
        "fullscreen": "f",
        "theater mode": "t",
        "miniplayer": "i",
        "close youtube": "ctrl+w"
    }

    for action, key in actions.items():
        if action in command:
            pyautogui.press(key)
            break
        
def take_note():
    speak("What would you like to note down?")
    time.sleep(1)  # Allow time for speech output to finish

    def process_note(note_content):
        if note_content and note_content != "none":
            with open("jani-notes.txt", "w") as file:
                file.write(note_content + "\n")
            speak("Your note has been saved.")
        else:
            speak("I couldn't hear your note. Please try again later.")

    takeCommand(callback=process_note)  # Capture note using an embedded function
        
            
def searchGoogle():
    speak("What do you want to search?")
    time.sleep(1)  # Allow time for speech to finish

    def process_search(query):
        if query and query != "none":
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching Google for {query}")
        else:
            speak("I didn't catch that. Please try again.")
    
    takeCommand(callback=process_search)  # Run takeCommand() with a callback



def closeGoogle():
    """Closes the last opened Google Chrome tab"""
    speak("Closing Google search tab.")
    pyautogui.hotkey("ctrl", "w")
    
def get_latest_headlines():
    try:
        url = 'https://news.google.com/topstories?hl=en-IN&gl=IN&ceid=IN:en'
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return ["Failed to fetch news"]

        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = []
        for item in soup.find_all('h3', limit=5):
            title = item.get_text(strip=True)
            headlines.append(title)

        if not headlines:
            headlines.append("No headlines found, website structure may have changed.")
        return headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return ["Error fetching news, please try again later."]

    
def processCommand(query):
        query = query.lower()
    
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=3)
            speak("According to Wikipedia")
            print(results)
            speak(results)
        
        elif 'open youtube' in query:
            openYouTube()

        elif 'search youtube' in query:
            search_query = query.replace("search youtube for", "").strip()
            searchYouTube(search_query)

        elif any(x in query for x in ["pause", "play", "mute", "unmute", "volume", "next", "previous", "fullscreen", "theater", "miniplayer", "close youtube"]):
            controlYouTube(query)
        
        elif 'open google' in query or 'search google' in query:
            searchGoogle()
            
        elif 'close google' in query:
            closeGoogle()
        
        elif 'open stack overflow' in query:
            speak("Opening Stack Overflow. Happy coding!")
            webbrowser.open("stackoverflow.com")
        
        elif 'play music' in query or "play song" in query:
            speak("Playing music")
            music_dir = r"C:\\Users\\Somu\\Music"
            songs = os.listdir(music_dir)
            print(songs)
            os.startfile(os.path.join(music_dir, songs[1]))
        
        elif 'the time' in query:
            try:
                current_time = datetime.datetime.now()
                strTime = current_time.strftime("%I:%M %p")
                speak(f"Sir, the time is {strTime}")
            except Exception as e:
                print(f"Error getting time: {e}")
                speak("Sorry, I'm having trouble getting the current time")
        
        # elif 'email to somashekar' in query:
        #     try:
        #         speak("What should I say?")
        #         content = takeCommand()
        #         to = "Receiver email address"
        #         sendEmail(to, content)
        #         speak("Email has been sent!")
        #     except Exception as e:
        #         print(e)
        #         speak("I am not able to send this email")
        
        elif 'exit' in query:
            speak("Thanks for giving me your time")
            exit()
        
        elif "who made you" in query or "who created you" in query:
            speak("I have been created by Somashekar.")
        
        elif 'joke' in query:
            speak(pyjokes.get_joke())
            
        elif "who are you" in query:
            speak("I am your virtual assistant created by Somashekar")
 
        elif 'reason for you' in query:
            speak("I was created as a Major project by Mister Somashekar ")
 
        elif 'change background' in query:
            ctypes.windll.user32.SystemParametersInfoW(20, 
                                                       0, 
                                                       "Location of wallpaper",
                                                       0)
            speak("Background changed successfully")
        
        # elif "calculate" in query:
        #     app_id = "Wolframalpha api id"
        #     client = wolframalpha.Client(app_id)
        #     indx = query.lower().split().index('calculate')
        #     query = query.split()[indx + 1:]
        #     res = client.query(' '.join(query))
        #     answer = next(res.results).text
        #     print("The answer is " + answer)
        #     speak("The answer is " + answer)
        
        elif 'search' in query or 'play' in query:
            query = query.replace("search", "").replace("play", "")
            webbrowser.open(query)
        
        elif 'lock window' in query:
            speak("Locking the device")
            ctypes.windll.user32.LockWorkStation()
        
        elif 'shutdown system' in query:
            speak("Shutting down system")
            subprocess.call('shutdown /p /f')
        
        elif 'restart' in query:
            subprocess.call(["shutdown", "/r"])
        
        elif "weather" in query:
            api_key = "API_KEY"
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            speak("City name")
            print("City name: ")
            city_name = takeCommand()
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            response = requests.get(complete_url)
            x = response.json()
            if x["cod"] != "404":
                y = x["main"]
                current_temperature = y["temp"]
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                speak(f"Temperature: {current_temperature} Kelvin, Pressure: {current_pressure} hPa, Humidity: {current_humidity}%, Description: {weather_description}")
            else:
                speak("City Not Found")
                
        elif "show news" in query or "today's news" in query:
            headlines = get_latest_headlines()
            news = "Here are the latest news headlines:\n" + "\n".join(f"{i+1}. {headline}" for i, headline in enumerate(headlines))
            print(news)
            speak(news)

        elif "read headlines" in query or "headlines" in query:
            headlines = get_latest_headlines()
            news = "Today's top headlines are:\n" + "\n".join(f"{i+1}. {headline}" for i, headline in enumerate(headlines))
            print(news)
            speak(news)

                
                
        # elif "send message " in query:
        #         # You need to create an account on Twilio to use this service
        #         account_sid = 'Account Sid key'
        #         auth_token = 'Auth token'
        #         client = Client(account_sid, auth_token)
 
        #         message = client.messages \
        #                         .create(
        #                             body = takeCommand(),
        #                             from_='Sender No',
        #                             to ='Receiver No'
        #                         )
 
        #         print(message.sid)
 
        elif "wikipedia" in query:
            webbrowser.open("wikipedia.com")
 
        elif "Good Morning" in query.lower():
            speak("A warm" +query)
            speak("How are you Mister")
            speak(assiname)
 
        # most asked question from google Assistant
        elif "will you be my gf" in query or "will you be my bf" in query:   
            speak("I'm not sure about that , may be you should give me some time")
 
        elif "how are you" in query:
            speak("I'm fine, glad you asked me that")
 
        elif "i love you" in query:
            speak("It's hard to understand")
 
        # elif "what is" in query or "who is" in query:
             
        #     # Use the same API key 
        #     # that we have generated earlier
        #     client = wolframalpha.Client("API_ID")
        #     res = client.query(query)
             
        #     try:
        #         print (next(res.results).text)
        #         speak (next(res.results).text)
        #     except StopIteration:
        #         print ("No results")
                
        elif "take a screenshot" in query or "take a photo" in query:
            # Create a folder to store screenshots if it doesn't exist
            screenshot_folder = "JANI-Screenshots"
            if not os.path.exists(screenshot_folder):
                os.makedirs(screenshot_folder)

            # Generate a unique filename using timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"jani_screenshot_{timestamp}.png"
            screenshot_path = os.path.join(screenshot_folder, screenshot_filename)

            # Capture and save the screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            # Confirm to the user
            speak(f"Screenshot saved to {screenshot_folder}")
            
        elif "write a note" in query or "take a note" in query:
            # speak("What should I write, sir?")
            # print("Waiting for note input...")  # Debug print
            # note = takeCommand()
            # print(f"Note received: {note}")  # Debug print
            
            # file = open('jani-notes.txt', 'w')

            # speak("Sir, should I include date and time?")
            # print("Waiting for date-time confirmation...")  # Debug print
            # snfm = takeCommand()
            # print(f"Confirmation received: {snfm}")  # Debug print

            # if 'yes' in snfm or 'sure' in snfm:
            #     strTime = datetime.datetime.now().strftime("%H:%M:%S")
            #     file.write(strTime + " :- " + note + "\n")
            # else:
            #     file.write(note + "\n")

            # file.close()
            # speak("Note saved successfully.")
            take_note()


        elif "show note" in query:
            speak("Showing Notes")
            
            try:
                with open("jani-notes.txt", "r") as file:
                    notes = file.read()
                    print(notes)

                speak("Would you like me to read it out?")
                read_choice = takeCommand()

                if 'yes' in read_choice or 'sure' in read_choice:
                    speak(notes)
                else:
                    speak("Okay, I won’t read it out loud.")

            except FileNotFoundError:
                speak("Sir, there are no saved notes.")
 
        # elif "" in query:
            # Command go here
            # For adding more commands
    

#running the endpoint here-


@app.post("/voice_command")
async def voice_command(task: BackgroundTasks, command: str):
    """Receives voice input asynchronously and processes commands"""
    task.add_task(processCommand, command)
    return {"message": "Processing voice command in background"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




#o run the voice commands locally- 
# if __name__ == '__main__':
#     # clear = lambda: os.system('cls')
#     # clear()
#     wishMe()
#     # username()
#     # create_gui()
#     while True:
#         processCommand(takeCommand())
    
