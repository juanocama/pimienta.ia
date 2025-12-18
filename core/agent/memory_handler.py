import re
from core.memory.memory_service import MemoryService


class MemoryHandler:
    """Maneja todas las operaciones relacionadas con memoria"""

    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service

    def handle_store(self, user_input: str) -> str:
        """Almacena un hecho general en memoria"""
        fact = re.sub(
            r'^(recuerda\s+que|recuerda)\s*',
            '',
            user_input,
            flags=re.I
        ).strip()

        self.memory.remember(fact)
        return "Listo. Lo recordaré."

    def handle_recall(self, user_input: str) -> str:
        """Recupera información de memoria"""
        recalled = self.memory.recall(user_input)
        return (
            f"Esto es lo que recuerdo:\n{recalled}"
            if recalled else
            "No recuerdo nada relevante todavía."
        )

    def handle_music_preference(self, user_input: str) -> tuple[bool, str | None]:
        """
        Detecta y almacena preferencias musicales.
        
        Returns:
            tuple: (is_preference, response)
        """
        lowered = user_input.lower()
        
        if not lowered.startswith("recuerda que me gusta"):
            return False, None

        preference = re.sub(
            r"^recuerda\s+que\s+me\s+gusta\s*",
            "",
            user_input,
            flags=re.I
        ).strip()
        
        self.memory.remember({
            "type": "music_preference",
            "value": preference
        })
        
        return True, f"Perfecto, recordaré que te gusta {preference} 🎵"