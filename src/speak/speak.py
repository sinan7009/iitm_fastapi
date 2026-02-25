import json
import random
import pyttsx3
import speech_recognition as sr
import os
import time
from google import genai
from google.genai import types

# -------------------------------
# Gemini API setup
# -------------------------------
# Replace with your actual AI Studio API key
client = genai.Client(api_key="AIzaSyBNKJZYl5ja-ZxJbmaxf5ZedvQzqdkopi4")


def ask_gemini(prompt):
    """
    Send user input to Gemini API via genai SDK and get response.
    Uses gemini-2.5-flash-lite model with a system instruction.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Answer clearly and concisely"
            )
        )
        speak(response)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return "Sorry, I could not get a response from the AI."


# -------------------------------
# Initialize TTS engine once
# -------------------------------
engine = pyttsx3.init(driverName='sapi5')
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower() or "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', engine.getProperty('rate') - 65)


def speak(text):
    """Speak text using pyttsx3"""
    print("🤖 Nexa says:", text)
    engine.say(text)
    engine.runAndWait()


# -------------------------------
# Load intents from JSON
# -------------------------------
speech_json_path = os.path.join(os.path.dirname(__file__), "speech.json")
if os.path.exists(speech_json_path):
    with open(speech_json_path, "r") as f:
        intents = json.load(f)
else:
    intents = {}


def get_intent_response(intent_type, **kwargs):
    """Get response text from intents JSON"""
    template = random.choice(intents[intent_type])
    text = template.format(**kwargs)
    print(f"💬 Speaking intent [{intent_type}]: {text}")
    speak(text)
    return text


# -------------------------------
# Listen function
# -------------------------------
def listen(timeout=5, phrase_time_limit=10):
    """Listen to the microphone and convert speech to text"""
    speak("Yes? I am listening for your question.")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🟢 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("🟡 Recognizing...")
            text = recognizer.recognize_google(audio)

            print(f"📝 You said: {text}")
            ask_gemini(text)
            return text
        except sr.WaitTimeoutError:
            print("⚠️ No speech detected.")
            return None
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"❌ Recognition error; {e}")
            return None


# -------------------------------
# Continuous assistant loop
# -------------------------------
TRIGGER_WORD = "friday"


def assistant_loop():
    speak("Hello! I am Nexa. Say 'Hey Nexa' to activate me.")

    while True:
        user_input = listen()
        if user_input:
            user_input_lower = user_input.lower()

            if TRIGGER_WORD in user_input_lower:


                # Listen for the actual question
                command = listen(timeout=5, phrase_time_limit=20)
                if command:
                    # Check intents first
                    intent_type = command.lower()
                    if intent_type in intents:
                        get_intent_response(intent_type)
                    else:
                        # Otherwise, send to Gemini API
                        ai_response = ask_gemini(command)
                        speak(ai_response)
                else:
                    speak("I didn't catch that. Could you repeat?")
            else:
                print("🔹 Trigger not detected, ignoring...")

        time.sleep(0.5)


if __name__ == "__main__":
    assistant_loop()