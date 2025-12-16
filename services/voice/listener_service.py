import speech_recognition as sr

class ListenerService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self) -> str:
        with self.microphone as source:
            print("🎙️ Escuchando...")
            audio = self.recognizer.listen(source)

        try:
            return self.recognizer.recognize_google(audio, language="es-ES")
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
