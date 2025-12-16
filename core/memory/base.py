from abc import ABC, abstractmethod

class Memory(ABC):

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def search(self, query: str) -> list[str]:
        pass
