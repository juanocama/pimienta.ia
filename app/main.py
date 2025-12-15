from pathlib import Path
import sys

# Ensure project root is on sys.path so local packages like `core` can be imported
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
from core.agent.agent import Agent

def main():
    agent = Agent()
    print("🎙️ Agente IA iniciado (escribe 'salir' para terminar)\n")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ("salir", "exit"):
            break

        response = agent.handle(user_input)
        print(f"Agente: {response}\n")


if __name__ == "__main__":
    main()


