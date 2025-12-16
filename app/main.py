from pathlib import Path
import sys

# Ensure project root is on sys.path so local packages like `core` can be imported
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from core.agent.agent import Agent
from services.voice.speaker_service import VoiceService
from services.voice.listener_service import ListenerService


def main():
    agent = Agent()

    # Crear servicios UNA sola vez
    voice = VoiceService(voice_index=0)
    listener = ListenerService()

    print("🎙️ Pimienta está lista. Di 'salir' para terminar.")

    while True:
        text = listener.listen()
        if not text:
            continue

        print(f"Tú: {text}")

        if text.lower().strip() == "salir":
            break

        try:
            response = agent.handle(text)

            # Verificar si la respuesta está vacía o es None
            if not response:
                response = "Lo siento, no entendí bien eso. ¿Puedes repetirlo?"

        except Exception as e:
            response = f"Ocurrió un error interno: {e}"

        # 🔊 REGLA DE ORO: si hay respuesta, SIEMPRE hablar
        print(f"Pimienta: {response}")
        voice.speak(response)


if __name__ == "__main__":
    main()


