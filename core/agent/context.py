class AgentContext:
    """
    Mantiene el contexto de la conversación.
    """
    def __init__(self):
        self.history: list[str] = []

    def add(self, role: str, message: str):
        self.history.append(f"{role}: {message}")

    def add_system(self, message: str):
        """
        Inserta un mensaje de sistema al inicio del contexto
        (para personalidad, reglas globales, etc.)
        """
        self.history.insert(0, f"SYSTEM: {message}")

    def get_context(self) -> str:
        return "\n".join(self.history[-10:])

