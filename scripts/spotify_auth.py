from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto o desde venv/.env si existe
ROOT = Path(__file__).resolve().parents[1]
for env_path in (ROOT / ".env", ROOT / "venv" / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break

# Obtener credenciales de Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Validar que las credenciales existen
if not SPOTIFY_CLIENT_ID:
    raise ValueError("SPOTIFY_CLIENT_ID no configurada en .env")
if not SPOTIFY_CLIENT_SECRET:
    raise ValueError("SPOTIFY_CLIENT_SECRET no configurada en .env")
if not SPOTIFY_REDIRECT_URI:
    raise ValueError("SPOTIFY_REDIRECT_URI no configurada en .env")

so = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state",
    cache_path=str(ROOT / '.spotify_cache'),
)

print('Abre esta URL en tu navegador y autoriza la app:')
print(so.get_authorize_url())
redirect = input('\nDespués de autorizar, pega aquí la URL completa de redirección:\n').strip()
qs = urlparse(redirect).query
code = parse_qs(qs).get('code', [None])[0]
if not code:
    print('No se encontró el parámetro code en la URL de redirección.')
else:
    token_info = so.get_access_token(code)
    print('Token exchange result keys:', list(token_info.keys()))
    print('Token guardado en:', str(ROOT / '.spotify_cache'))
    print('Ahora deberías poder reproducir música desde la app.')