from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.llm.gemini_client import GeminiClient

def main():
    llm = GeminiClient()
    
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ("salir", "exit"):
            break
        
        response = llm.generate(user_input)
        print(f"Gemini: {response}")

if __name__ == "__main__":
    main()

