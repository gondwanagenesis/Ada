import asyncio
import speech_recognition as sr
import pyttsx3
from module import GroqModule

class SpeechModule:
    def __init__(self, whisper_api_key):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.whisper_module = GroqModule('Whisper', '', whisper_api_key)

    async def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        
        try:
            # Use Whisper API for speech recognition
            text = await self.whisper_module.process(audio.get_wav_data())
            return text
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
