import pyttsx3
import pyautogui
import psutil
import pyjokes
import speech_recognition as sr
import json
import requests
import geocoder
from difflib import get_close_matches


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
g = geocoder.ip('me')
data = json.load(open('data.json'))

def speak(audio) -> None:
        engine.say(audio)
        engine.runAndWait()

def screenshot() -> None:
    img = pyautogui.screenshot()
    img.save('path of folder you want to save/screenshot.png')

def cpu() -> None:
    usage = str(psutil.cpu_percent())
    speak("CPU is at"+usage)

    battery = psutil.sensors_battery()
    speak("battery is at")
    speak(battery.percent)

def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])
        
# def takeCommand(activation_phrase="take command") -> str:
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Say the activation phrase to begin...")

#         while True:
#             try:
#                 # Continuously listen until the activation phrase is heard
#                 audio = r.listen(source)
#                 command = r.recognize_google(audio, language="en-in").lower()
#                 if activation_phrase in command:
#                     speak("I am ready for your command.")
#                     print("Listening for your command...")

#                     # Now start listening for the actual command
#                     audio = r.listen(source)
#                     command = r.recognize_google(audio, language="en-in")
#                     print(f"User said: {command}")
#                     return command

#             except Exception as e:
#                 print("Couldn't understand. Listening again...")
                
# def takeCommand() -> str:
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print('Listening...')
#         r.pause_threshold = 1
#         r.energy_threshold = 494
#         r.adjust_for_ambient_noise(source, duration=1.5)
#         audio = r.listen(source)

#     try:
#         print('Recognizing..')
#         query = r.recognize_google(audio, language='en-in')
#         print(f'User said: {query}\n')

#     except Exception as e:
#         # print(e)

#         print('Say that again please...')
#         return 'None'
#     return query

def weather():
    api_url = "https://fcc-weather-api.glitch.me/api/current?lat=" + str(g.latlng[0]) + "&lon=" + str(g.latlng[1])

    try:
        data = requests.get(api_url)
        if data.status_code == 200:  # Check if the request was successful
            data_json = data.json()
            
            if data_json['cod'] == 200:
                main = data_json['main']
                wind = data_json['wind']
                weather_desc = data_json['weather'][0]
                
                speak(str(data_json['coord']['lat']) + 'latitude' + str(data_json['coord']['lon']) + 'longitude')
                speak('Current location is ' + data_json['name'] + data_json['sys']['country'] + 'dia')
                speak('Weather type ' + weather_desc['main'])
                speak('Wind speed is ' + str(wind['speed']) + ' metres per second')
                speak('Temperature: ' + str(main['temp']) + ' degrees Celsius')
                speak('Humidity is ' + str(main['humidity']))
            else:
                speak("Unable to retrieve weather information. Please try again later.")
        else:
            speak("Error in fetching weather data. Status code: " + str(data.status_code))
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
