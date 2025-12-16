import pyttsx3

class VoiceService:
    def __init__(self, voice_index: int = 0, rate: int = 175):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")

        if voices:
            self.engine.setProperty("voice", voices[voice_index].id)

        self.engine.setProperty("rate", rate)

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
