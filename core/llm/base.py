from abc import ABC, abstractmethod

class LLMClient(ABC):
    """
    Interfaz base para cualquier modelo de lenguaje.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
