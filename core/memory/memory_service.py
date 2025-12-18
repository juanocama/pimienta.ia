class MemoryService:
    def __init__(self, memory):
        self.memory = memory

    def remember(self, data):
        if isinstance(data, dict):
            key = data.get("type", "fact")
            value = data.get("value", str(data))
            self.memory.save(key, value)
            return

        text = str(data)
        lowered = text.lower().strip()

        if lowered.startswith("me gusta"):
            preference = text[len("me gusta"):].strip()
            if preference:
                self.memory.save("music_preference", preference)
                return

        self.memory.save("fact", text)

    def recall(self, query: str) -> str | None:
        lowered = query.lower()

        music_keywords = (
            "me gusta", "gustos", "música", "musica",
            "preferencias", "favorito", "favoritos",
            "escucho", "escuchar"
        )
        
        if any(kw in lowered for kw in music_keywords):
            results = self.memory.get_by_key("music_preference")
            
            if results:
                if len(results) == 1:
                    return f"Te gusta {results[0]}"
                else:
                    items = ", ".join(results[:-1]) + f" y {results[-1]}"
                    return f"Te gusta {items}"
            
            return None

        results = self.memory.search(query)
        
        if results:
            return "\n".join(results)
        
        return None

    def get_music_preferences(self) -> list[str]:
        return self.memory.get_by_key("music_preference") or []

    def get_all_facts(self) -> list[str]:
        return self.memory.get_by_key("fact") or []

    def clear_music_preferences(self) -> int:
        return self.memory.delete_by_key("music_preference")

    def clear_all_memories(self):
        self.memory.clear_all()