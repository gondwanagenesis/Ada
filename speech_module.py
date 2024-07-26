import asyncio
import speech_recognition as sr
import pyttsx3
import aiohttp
import io

class SpeechModule:
    def __init__(self, whisper_api_key):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.whisper_api_key = whisper_api_key
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"

    async def listen(self):
        try:
            with sr.Microphone() as source:
                print("Microphone initialized. Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Audio captured. Processing...")
            # Use Whisper API for speech recognition
            text = await self.transcribe_audio(audio.get_wav_data())
            return text.strip()  # Strip any leading/trailing whitespace
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None

    async def transcribe_audio(self, audio_data):
        headers = {
            "Authorization": f"Bearer {self.whisper_api_key}",
            "Content-Type": "application/octet-stream"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                data=audio_data,
                params={"model": "whisper-1", "language": "en"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('text', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
