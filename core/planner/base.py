from abc import ABC, abstractmethod

class Planner(ABC):
    @abstractmethod
    def plan(self, context: str) -> dict:
        """Devuelve un plan en formato JSON"""
        pass
