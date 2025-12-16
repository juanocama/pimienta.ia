import os
from pathlib import Path
from dotenv import load_dotenv

# Try loading a .env from project root first, then fall back to venv/.env
ROOT = Path(__file__).resolve().parents[2]
env_loaded = load_dotenv(ROOT / ".env")
if not env_loaded:
    # fallback to venv/.env if present
    venv_env = ROOT / "venv" / ".env"
    if venv_env.exists():
        load_dotenv(venv_env)


class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


settings = Settings()
