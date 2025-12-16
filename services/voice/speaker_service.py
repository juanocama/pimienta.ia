import pyttsx3

class VoiceService:
    def __init__(self, voice_index: int = 0):
        self.voice_index = voice_index

    def speak(self, text: str):
        if not text:
            return

        # 🔥 CREAR EL MOTOR CADA VEZ (clave)
        engine = pyttsx3.init()

        voices = engine.getProperty("voices")
        if voices and self.voice_index < len(voices):
            engine.setProperty("voice", voices[self.voice_index].id)

        engine.setProperty("rate", 170)  # velocidad natural
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

        # 🔥 CERRAR explícitamente
        engine.stop()
