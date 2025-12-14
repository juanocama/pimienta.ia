import google.generativeai as genai
from core.llm.base import LLMClient
from infrastructure.config.settings import settings
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto o desde venv/.env si existe
ROOT = Path(__file__).resolve().parents[2]
for env_path in (ROOT / ".env", ROOT / "venv" / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break

# Valor por defecto (puede ser None si no está configurada)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiClient(LLMClient):
    def __init__(self, api_key: str | None = None):
        # Prioriza el api_key pasado, luego la variable cargada
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
