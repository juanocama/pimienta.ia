from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
import os
from dotenv import load_dotenv
import spotipy

# Cargar .env desde la raíz del proyecto o desde venv/.env si existe
ROOT = Path(__file__).resolve().parents[2]
for env_path in (ROOT / ".env", ROOT / "venv" / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break

# Obtener credenciales de Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')


class SpotifyService:
    def __init__(self):
        # Validar credenciales
        if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI]):
            raise ValueError("Credenciales de Spotify no configuradas en .env")
        
        # Configurar autenticación
        self.auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-read-playback-state,user-modify-playback-state",
            cache_path=str(ROOT / '.spotify_cache'),
        )
        
        # Crear cliente de Spotify
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def play(self, query: str = None):
        """Reproduce música en Spotify"""
        try:
            if query:
                # Buscar la canción/artista
                results = self.sp.search(q=query, limit=1, type='track')
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    self.sp.start_playback(uris=[track_uri])
                    return f"Reproduciendo: {results['tracks']['items'][0]['name']}"
                else:
                    return f"No encontré resultados para: {query}"
            else:
                # Reanudar reproducción
                self.sp.start_playback()
                return "Reproducción reanudada"
        except Exception as e:
            raise Exception(f"Error al reproducir: {str(e)}")

    def pause(self):
        """Pausa la reproducción"""
        try:
            self.sp.pause_playback()
            return "Reproducción pausada"
        except Exception as e:
            raise Exception(f"Error al pausar: {str(e)}")

    def next(self):
        """Salta a la siguiente canción"""
        try:
            self.sp.next_track()
            return "Siguiente canción"
        except Exception as e:
            raise Exception(f"Error al saltar canción: {str(e)}")