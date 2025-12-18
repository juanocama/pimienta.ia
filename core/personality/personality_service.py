from core.personality.personality import Personality
from core.memory.memory_service import MemoryService

class PersonalityService:
    KEY = "personality"

    def __init__(self, memory: MemoryService):
        self.memory = memory

    def load(self) -> Personality:
        data = self.memory.recall("personalidad")
        if not data:
            return Personality()

        try:
            return Personality(**data)
        except Exception:
            return Personality()

    def save(self, personality: Personality):
        self.memory.memory.save(self.KEY, personality.__dict__)
