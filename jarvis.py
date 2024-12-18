import pyttsx3
import wikipedia
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import smtplib
from news import speak_news, getNewsUrl
from OCR import OCR
from diction import translate,takeCommand
from helpers import *
from youtube import youtube
from sys import platform
import aifc
import getpass
import cv2

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# print(voices[0].id)


def load_all_trainers(recognizer, trainer_folder_path):
    """Load all trainer.yml files from a specified folder."""
    trainer_files = [os.path.join(trainer_folder_path, f) for f in os.listdir(trainer_folder_path) if f.endswith(".yml")]
    for trainer_file in trainer_files:
        recognizer.read(trainer_file)
    print(f"Loaded {len(trainer_files)} trainer files.")
    

class Jarvis:
    def __init__(self) -> None:
        if platform == "linux" or platform == "linux2":
            self.chrome_path = r'/usr/bin/google-chrome'

        # elif platform == "darwin":
        #     self.chrome_path = 'open -a /Applications/Google\ Chrome.app'

        elif platform == "win32":
            self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        else:
            print('Unsupported OS')
            exit(1)
        webbrowser.register(
            'chrome', None, webbrowser.BackgroundBrowser(self.chrome_path)
        )


    def get_location_from_ip(self):
        try:
            response = requests.get("https://ipapi.co/json/")
            if response.status_code == 200:
                data = response.json()
                return data.get('latitude'), data.get('longitude')
            else:
                speak("Error fetching location from IP service.")
                return None, None
        except requests.exceptions.RequestException as e:
            speak("Unable to retrieve location from the IP service.")
            print(f"Exception: {e}")
            return None, None


    def wishMe(self):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            speak("Good Morning SIR")
        elif hour >= 12 and hour < 18:
            speak("Good Afternoon SIR")
        else:
            speak("Good Evening SIR")

        speak("Retrieving your location for weather updates.")
        latitude, longitude = self.get_location_from_ip()
        if latitude and longitude:
            global g
            g.latlng = (latitude, longitude)  # Set location globally
            weather()
        else:
            speak("Unable to fetch location. Weather updates unavailable.")
        
        speak("I am JARVIS. Please tell me how I can assist you, SIR.")

        takeCommand()

    def sendEmail(self, to, content) -> None:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('email', 'password')
        server.sendmail('email', to, content)
        server.close()

    def execute_query(self, query):
        # TODO: make this more concise
        if 'wikipedia' in query:
            speak('Searching Wikipedia....')
            query = query.replace('wikipedia', '')
            results = wikipedia.summary(query, sentences=2)
            speak('According to Wikipedia')
            print(results)
            speak(results)
        elif 'youtube downloader' in query:
            exec(open('youtube_downloader.py').read())
            
        
            
        elif 'voice' in query:
            if 'female' in query:
                engine.setProperty('voice', voices[1].id)
            else:
                engine.setProperty('voice', voices[0].id)
            speak("Hello Sir, I have switched my voice. How is it?")

        if 'jarvis are you there' in query:
            speak("Yes Sir, at your service")
        if 'jarvis who made you' in query:
            speak("Yes Sir, my master build me in AI")
            
         

        elif 'open youtube' in query:

            webbrowser.get('chrome').open_new_tab('https://youtube.com')
            
        elif 'open amazon' in query:
            webbrowser.get('chrome').open_new_tab('https://amazon.com')

        elif 'cpu' in query:
            cpu()

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'open google' in query:
            webbrowser.get('chrome').open_new_tab('https://google.com')

        elif 'open stack overflow' in query:
            webbrowser.get('chrome').open_new_tab('https://stackoverflow.com')

        elif 'play music' in query:
            os.startfile("D:\\RoiNa.mp3")

        elif 'search youtube' in query:
            speak('What you want to search on Youtube?')
            youtube(takeCommand())
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f'Sir, the time is {strTime}')

        elif 'search' in query:
            speak('What do you want to search for?')
            search = takeCommand()
            url = 'https://google.com/search?q=' + search
            webbrowser.get('chrome').open_new_tab(
                url)
            speak('Here is What I found for' + search)

        elif 'location' in query:
            speak('What is the location?')
            location = takeCommand()
            url = 'https://google.nl/maps/place/' + location + '/&amp;'
            webbrowser.get('chrome').open_new_tab(url)
            speak('Here is the location ' + location)

        elif 'your master' in query:
            if platform == "win32" or "darwin":
                speak('Soma is my master. He created me couple of days ago')
            elif platform == "linux" or platform == "linux2":
                name = getpass.getuser()
                speak(name, 'is my master. He is running me right now')

        elif 'your name' in query:
            speak('My name is JANI')
        elif 'who made you' in query:
            speak('I was created by my AI master in 2024')
            
        elif 'stands for' in query:
            speak('J.A.N.I stands for JUST IN TIME ASSISTANT FOR NECESSARY INSIGHTS.')
        elif 'open code' in query:
            if platform == "win32":
                os.startfile(
                    "C:\\Users\\gs935\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
            elif platform == "linux" or platform == "linux2" or "darwin":
                os.system('code .')

        elif 'shutdown' in query:
            if platform == "win32":
                os.system('shutdown /p /f')
            elif platform == "linux" or platform == "linux2" or "darwin":
                os.system('poweroff')

        elif 'cpu' in query:
            cpu()
        elif 'your friend' in query:
            speak('My friends are Google assisstant alexa and siri')

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'github' in query:
            webbrowser.get('chrome').open_new_tab(
                'https://github.com/gauravsingh9356')

        elif 'remember that' in query:
            speak("what should i remember sir")
            rememberMessage = takeCommand()
            speak("you said me to remember"+rememberMessage)
            remember = open('data.txt', 'w')
            remember.write(rememberMessage)
            remember.close()

        elif 'do you remember anything' in query:
            remember = open('data.txt', 'r')
            speak("you said me to remember that" + remember.read())

        elif 'sleep' in query:
            sys.exit()

        elif 'dictionary' in query:
            speak('What you want to search in your intelligent dictionary?')
            translate(takeCommand())

        elif 'news' in query:
            speak('Ofcourse sir..')
            speak_news()
            speak('Do you want to read the full news...')
            test = takeCommand()
            if 'yes' in test:
                speak('Ok Sir, Opening browser...')
                webbrowser.open(getNewsUrl())
                speak('You can now read the full news from this website.')
            else:
                speak('No Problem Sir')

        elif 'voice' in query:
            if 'female' in query:
                engine.setProperty('voice', voices[0].id)
            else:
                engine.setProperty('voice', voices[1].id)
            speak("Hello Sir, I have switched my voice. How is it?")

        elif 'email to gaurav' in query:
            try:
                speak('What should I say?')
                content = takeCommand()
                to = 'email'
                self.sendEmail(to, content)
                speak('Email has been sent!')

            except Exception as e:
                speak('Sorry sir, Not able to send email at the moment')


def wakeUpJARVIS():
    bot_ = Jarvis()
    bot_.wishMe()
    while True:
        print("Waiting for query...")
        query = takeCommand().lower()
        print(f"User Query: {query}")
        if query != "none":
            bot_.execute_query(query)

               

if __name__ == '__main__':
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # Local Binary Patterns Histograms
    trainer_folder_path = r'C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\trainer'
    load_all_trainers(recognizer, trainer_folder_path)  # Load all trainer.yml files

    cascadePath = r"C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX  # Font type

    id = 1  # Number of persons to recognize
    names = ['', 'soma', 'anjan']  # Names corresponding to IDs

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)  # Set video FrameWidth
    cam.set(4, 480)  # Set video FrameHeight

    minW = 0.1 * cam.get(3)  # Minimum window size width
    minH = 0.1 * cam.get(4)  # Minimum window size height

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            id, accuracy = recognizer.predict(gray[y:y+h, x:x+w])

            if accuracy < 100:
                speak(f"Optical Face Recognition Done. Welcome {names[id]}!")
                cam.release()
                cv2.destroyAllWindows()
                wakeUpJARVIS()
            else:
                speak("Optical Face Recognition Failed")
                break

    
