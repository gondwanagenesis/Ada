import asyncio
import speech_recognition as sr
import pyttsx3
from module import GroqModule
import numpy as np
import wave
import io

class SpeechModule:
    def __init__(self, whisper_api_key):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.whisper_module = GroqModule('Whisper', '', whisper_api_key)

    async def listen(self):
        try:
            with sr.Microphone() as source:
                print("Microphone initialized. Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("Audio captured. Processing...")
            # Compress audio data
            compressed_audio = self.compress_audio(audio.get_wav_data())
            # Use Whisper API for speech recognition
            text = await self.whisper_module.process(compressed_audio)
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

    def compress_audio(self, audio_data):
        # Convert WAV data to numpy array
        with io.BytesIO(audio_data) as wav_io:
            with wave.open(wav_io, 'rb') as wav_file:
                channels = wav_file.getnchannels()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                audio_array = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)

        # Downsample the audio (reduce sample rate by factor of 4)
        downsampled = audio_array[::4]

        # Reduce bit depth from 16-bit to 8-bit
        downsampled_8bit = (downsampled / 256).astype(np.int8)

        # Convert back to WAV format
        with io.BytesIO() as compressed_io:
            with wave.open(compressed_io, 'wb') as compressed_wav:
                compressed_wav.setnchannels(channels)
                compressed_wav.setsampwidth(1)  # 8-bit audio
                compressed_wav.setframerate(framerate // 4)
                compressed_wav.writeframes(downsampled_8bit.tobytes())
            return compressed_io.getvalue()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
