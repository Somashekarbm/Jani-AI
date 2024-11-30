import pyttsx3
import pyautogui
import psutil
import pyjokes
import speech_recognition as sr
import json
import requests
import geocoder
from difflib import get_close_matches
from diction import takeCommand
import os


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
g = geocoder.ip('me')
data = json.load(open('data.json'))

def speak(audio) -> None:
        engine.say(audio)
        engine.runAndWait()

def screenshot() -> None:
    # Define the directory where screenshots will be saved
    screenshot_dir = r"C:\Users\Somu\Pictures\Screenshots\JarvisScreenshots"

    # Get a list of existing files in the directory
    existing_files = os.listdir(screenshot_dir)

    # Count the number of files to generate the next image number
    cnt = len([f for f in existing_files if f.endswith('.png')])

    # Take a screenshot
    img = pyautogui.screenshot()

    # Save the screenshot with a unique filename
    img.save(os.path.join(screenshot_dir, f"image{cnt + 1}.png"))
    print(f"Screenshot saved as image{cnt + 1}.png")

def cpu() -> None:
    usage = str(psutil.cpu_percent())
    speak("CPU is at"+usage)

    battery = psutil.sensors_battery()
    speak("battery is at")
    speak(battery.percent)

def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])
        
                

def weather():
    if not hasattr(g, 'latlng') or not g.latlng:
        speak("Location information is not available.")
        return

    lat, lon = g.latlng
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if 'current_weather' in data:
                current_weather = data['current_weather']
                temperature = current_weather['temperature']
                wind_speed = current_weather['windspeed']
                weather_desc = current_weather['weathercode']  # This can be mapped to descriptions
                speak(f"The current temperature is {temperature} degrees Celsius.")
                speak(f"The wind speed is {wind_speed} kilometers per hour.")
                speak(f"The weather code indicates: {weather_desc}.")
            else:
                speak("Unable to retrieve detailed weather information. Please try again later.")
        else:
            speak(f"Error fetching weather data. HTTP Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        speak("There was an error connecting to the weather service.")
        print(f"Exception: {e}")

        


def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak('Did you mean ' + x +
              ' instead,  respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("We didn't understand your entry.")

    else:
        speak("Word doesn't exist. Please double check it.")
