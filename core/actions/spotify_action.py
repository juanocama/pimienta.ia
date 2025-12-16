from core.actions.base_action import Action as BaseAction
from typing import Optional


def _get_spotify_service():
    # local import to avoid import-time issues and keep dependency optional
    from services.spotify.spotify_service import SpotifyService
    try:
        return SpotifyService()
    except Exception:
        # If Spotify cannot be initialized (missing credentials), return a no-op shim
        class _FakeSpotify:
            def play(self):
                return "[spotify] play (noop)"

            def pause(self):
                return "[spotify] pause (noop)"

            def next(self):
                return "[spotify] next (noop)"

        return _FakeSpotify()


class SpotifyAction(BaseAction):
    def __init__(self, spotify_service: Optional[object] = None):
        # Allow injecting a SpotifyService instance for testing or reuse.
        if spotify_service is None:
            spotify_service = _get_spotify_service()
        self.spotify = spotify_service

    def execute(self, params: dict) -> str:
        command = params.get("command")
        query = params.get("query")

        if command == "play":
            # if spotify service implements play(query), pass the query
            try:
                if query:
                    self.spotify.play(query)
                    return f"🎵 Reproduciendo: {query}"
                else:
                    self.spotify.play()
                    return "🎵 Reproduciendo música en Spotify."
            except Exception:
                return "No pude reproducir en Spotify (verifica configuración)."

        if command == "pause":
            try:
                self.spotify.pause()
                return "⏸ Música pausada."
            except Exception:
                return "No pude pausar la reproducción."

        if command == "next":
            try:
                self.spotify.next()
                return "⏭ Siguiente canción."
            except Exception:
                return "No pude saltar a la siguiente canción."

        return "No entendí qué hacer con Spotify."
