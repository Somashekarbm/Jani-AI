from vosk import Model, KaldiRecognizer
import pyttsx3
import wave
import pyaudio
import json
from difflib import get_close_matches

# Load your dictionary data
data = json.load(open('data.json'))

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    # Load the Vosk model (ensure the path is correct)
    model = Model(r"C:\Users\Somu\Desktop\J.A.R.V.I.S-master\vosk-model-small-en-us-0.15")  # Replace with your model path
    recognizer = KaldiRecognizer(model, 16000)

    # Setup the microphone input
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")
    try:
        # Give a timeout of 10 seconds
        for _ in range(int(10 * 16000 / 4000)):  # Adjust loop iterations to ~10 seconds
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                stream.stop_stream()
                stream.close()
                p.terminate()
                text = result.get("text", "")
                if text.strip() == "":
                    print("No voice detected.")
                    return "None"
                print(f"Recognized: {text}")
                return text
        print("Timeout reached. No input detected.")
        return "None"
    except Exception as e:
        print(f"Error during recognition: {e}")
        stream.stop_stream()
        stream.close()
        p.terminate()
        return "None"


def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak(f'Did you mean {x} instead? Respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("I did not understand your entry.")
    else:
        speak("Word doesn't exist. Please double check it.")

if __name__ == '__main__':
    word_to_translate = takeCommand()  # Use takeCommand to get the input word
    translate(word_to_translate)
