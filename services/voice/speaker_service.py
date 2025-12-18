import asyncio
import edge_tts
import pygame
import io
import sys

class VoiceService:
    def __init__(self, voice_index: int = 0):
        """
        Inicializa el servicio de voz de Edge.
        Mantenemos 'voice_index' para no romper el main.py original.
        """
        # Mapeo simple: si el index es 0 usamos voz femenina, si es 1 masculina
        self.voices = ["es-MX-DaliaNeural", "es-MX-JorgeNeural"]
        
        if voice_index < len(self.voices):
            self.voice = self.voices[voice_index]
        else:
            self.voice = self.voices[0]

        # Inicializar el mezclador de audio una sola vez
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def speak(self, text: str):
        if not text or not text.strip():
            return

        # Intentar obtener el loop actual de manera segura para Python 3.13
        try:
            # En versiones modernas, si no hay un loop en el hilo actual, 
            # creamos uno nuevo específicamente para la tarea
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_and_play(text))
            loop.close()
        except Exception as e:
            print(f"❌ Error en el ciclo de voz: {e}")

    async def _generate_and_play(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        
        # Usamos un buffer de memoria para no guardar archivos en disco
        audio_data = io.BytesIO()
        
        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])

            audio_data.seek(0)

            # Reproducir con pygame
            pygame.mixer.music.load(audio_data, "mp3")
            pygame.mixer.music.play()

            # Bloquear hasta que termine de hablar
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"❌ Error al procesar audio de Edge-TTS: {e}")
        finally:
            audio_data.close()

# Prueba rápida
if __name__ == "__main__":
    v = VoiceService(voice_index=0)
    v.speak("Probando la integración final con el sistema Pimienta.")