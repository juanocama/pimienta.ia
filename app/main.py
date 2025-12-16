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
    voice = VoiceService(voice_index=0)
    listener = ListenerService()

    print("🎙️ Pimienta está lista. Di 'salir' para terminar.")

    while True:
        text = listener.listen()
        if not text:
            continue

        print(f"Tú: {text}")

        if "salir" in text.lower():
            break

        response = agent.handle(text)
        print(f"Pimienta: {response}")
        voice.speak(response)

if __name__ == "__main__":
    main()



