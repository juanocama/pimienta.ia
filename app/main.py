from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from core.agent.agent import Agent
from services.voice.speaker_service import VoiceService
from services.voice.listener_service import ListenerService


def main():
    agent = Agent()
    voice = VoiceService(voice_index=0)
    listener = ListenerService()

    print("🎙️ Pimienta está lista. Di 'pimienta' para activarme o 'salir' para terminar.")

    while True:
        text = listener.listen()
        if not text:
            continue

        print(f"Tú: {text}")

        if text.lower().strip() == "salir":
            print("👋 ¡Hasta luego!")
            break

        try:
            response = agent.handle(text)
            if not response or response.strip() == "":
                continue

        except Exception as e:
            response = f"Ocurrió un error interno: {e}"
            print(f"❌ Error: {e}")

        # 🔊 Solo hablar si hay respuesta válida
        print(f"Pimienta: {response}")
        voice.speak(response)


if __name__ == "__main__":
    main()


