class IntentRouter:
    """
    Decide qué modelo debe manejar la petición.
    """

    ACTION_KEYWORDS = [
        "pon", "reproduce", "abre", "guarda", "recuerda",
        "crea", "ejecuta", "haz"
    ]

    def route(self, user_input: str) -> str:
        text = user_input.lower()
        for kw in self.ACTION_KEYWORDS:
            if kw in text:
                return "ACTION"
        return "THINK"
