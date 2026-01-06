from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
import os
from dotenv import load_dotenv
import spotipy
from typing import Optional

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
            scope="user-read-playback-state,user-modify-playback-state,user-library-read",
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

    def get_active_device(self) -> Optional[str]:
        """Return an active device id or None if no active device found."""
        try:
            devices = self.sp.devices()
            items = devices.get('devices', [])
            for d in items:
                if d.get('is_active'):
                    return d.get('id')
            if items:
                return items[0].get('id')
        except Exception:
            return None

    def reproducir_liked_songs(self, device_id: Optional[str] = None) -> int:
        """Play the user's saved (liked) tracks. Returns number of tracks queued/played.

        If `device_id` is None, attempt to use an active device.
        Raises exceptions from Spotipy on failure.
        """
        # import typing locally to avoid top-level changes if typing not available
        from typing import List

        if device_id is None:
            device_id = self.get_active_device()

        uris: List[str] = []
        results = self.sp.current_user_saved_tracks(limit=50)

        while results:
            for item in results.get('items', []):
                track = item.get('track')
                if track and track.get('uri'):
                    uris.append(track['uri'])
            if results.get('next'):
                results = self.sp.next(results)
            else:
                break

        if not uris:
            return 0

        # start_playback supports up to 100 URIs; use first 100
        chunk = uris[:100]
        if device_id:
            self.sp.start_playback(device_id=device_id, uris=chunk)
        else:
            self.sp.start_playback(uris=chunk)

        return len(uris)

    # Compatibility wrappers expected by `SpotifyAction`
    def play_liked(self) -> str:
        """Wrapper to play liked songs and return a user-friendly message."""
        try:
            count = self.reproducir_liked_songs()
            if count == 0:
                return "No tienes canciones en 'Me gusta'."
            return f"🎵 Reproduciendo tus {count} canciones guardadas."
        except Exception as e:
            raise Exception(f"Error reproduciendo 'Me gusta': {e}")

    def play_dj(self) -> str:
        """Placeholder for a DJ-style playback (not implemented)."""
        # Implement custom DJ logic later; for now, try to resume playback
        try:
            self.sp.start_playback()
            return "Iniciando modo DJ (reproducción estándar)."
        except Exception as e:
            raise Exception(f"Error iniciando DJ: {e}")