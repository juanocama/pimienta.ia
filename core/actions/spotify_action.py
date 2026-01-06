from core.actions.base_action import Action as BaseAction
from typing import Optional


def _get_spotify_service():
    from services.spotify.spotify_service import SpotifyService
    try:
        return SpotifyService()
    except Exception:
        class _FakeSpotify:
            def play(self, *_): return "[spotify noop]"
            def pause(self): return "[spotify noop]"
            def next(self): return "[spotify noop]"
            def play_liked(self): return "[spotify liked noop]"
            def play_dj(self): return "[spotify dj noop]"
        return _FakeSpotify()


class SpotifyAction(BaseAction):
    def __init__(self, spotify_service: Optional[object] = None):
        self.spotify = spotify_service or _get_spotify_service()

    def execute(self, params: dict) -> str:
        command = params.get("command")
        query = params.get("query")

        try:
            if command == "play":
                return self.spotify.play(query)

            if command == "pause":
                return self.spotify.pause()

            if command == "next":
                return self.spotify.next()

            if command == "play_liked":
                return self.spotify.play_liked()

            if command == "play_dj":
                return self.spotify.play_dj()

        except Exception:
            return "No pude controlar Spotify."

        return "Comando de Spotify no reconocido."

