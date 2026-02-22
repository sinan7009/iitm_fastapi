import json
import random
from datetime import datetime
import pyttsx3
# Initialize the text-to-speech engine
engine = pyttsx3.init()
import os

# # Set female voice
# voices = engine.getProperty('voices')
# for voice in voices:
#     if "female" in voice.name.lower() or "zira" in voice.name.lower():  # Windows example
#         engine.setProperty('voice', voice.id)
#         break
#
# # Set slow speaking rate
# rate = engine.getProperty('rate')
# engine.setProperty('rate', rate - 65)  # reduce by 100 (default is ~200)


def speak(text):
    engine = pyttsx3.init(driverName='sapi5')
    voices = engine.getProperty('voices')
    for voice in voices:
        if "zira" in voice.name.lower() or "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 65)
    print("speaking", text)
    engine.say(text)
    engine.runAndWait()
    print("✅ Finished speaking")



# Load greetings from JSON
speech_json_path = os.path.join(os.path.dirname(__file__), "speech.json")
with open(speech_json_path, "r") as f:
    intents = json.load(f)


def get_intent_response(intent_type, **kwargs):
    print(kwargs)
    template = random.choice(intents[intent_type])
    text = template.format(**kwargs)
    print(f"💬 Speaking intent [{intent_type}]: {text}")
    speak(text)
    return text

