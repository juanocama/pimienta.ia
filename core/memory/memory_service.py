class MemoryService:
    def __init__(self, memory):
        self.memory = memory

    def remember(self, text: str):
        # Simple extraction: if the text indicates a preference like "me gusta X",
        # store it under the key 'gustos' with the value X. Otherwise store as generic fact.
        lowered = text.lower().strip()
        if lowered.startswith("me gusta"):
            # store what's after 'me gusta'
            value = text[len("me gusta"):].strip()
            if value:
                self.memory.save("gustos", value)
                return
        # fallback: generic fact
        self.memory.save("fact", text)

    def recall(self, text: str) -> str | None:
        lowered = text.lower()

        # If the query is about likes/preferences, return stored 'gustos'
        if "me gusta" in lowered or "musica" in lowered or "música" in lowered or "gustos" in lowered:
            results = self.memory.get_by_key("gustos")
            if results:
                return "\n".join(results)
            return None

        # otherwise try a free-text search
        results = self.memory.search(text)
        if results:
            return "\n".join(results)
        return None
