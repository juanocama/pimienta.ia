import re
from core.agent.mode import AgentMode


class IntentRouter:
    """
    Decide QUÉ quiere hacer el usuario (intent)
    y CÓMO debe manejarse el mensaje (mode).
    """

    # -------------------------------------------------
    # MODE ROUTING (alto nivel)
    # -------------------------------------------------
    def route_mode(self, text: str) -> AgentMode:
        """
        Decide si el input es:
        - COMMAND: acción directa (Spotify, etc.)
        - THINK: razonamiento explícito
        - CONVERSATION: charla normal
        """
        lowered = text.lower()

        # Comandos directos (no requieren LLM conversacional)
        if any(w in lowered for w in (
            "pausa", "pause", "pausar",
            "pon", "reproduce", "reproducir", "play",
            "siguiente", "next", "skip",
            "continúa", "continuar", "reanuda", "resume"
        )):
            return AgentMode.COMMAND

        # Peticiones explícitas de razonamiento
        if any(w in lowered for w in (
            "piensa", "analiza", "razona", "reflexiona"
        )):
            return AgentMode.THINK

        return AgentMode.CONVERSATION

    # -------------------------------------------------
    # INTENT ROUTING (detalle)
    # -------------------------------------------------
    def route(self, text: str) -> str:
        """
        Devuelve el intent lógico para el Agent.
        """
        lowered = text.lower().strip()

        # -------- PRESENTATION --------
        presentation_triggers = [
            "quién eres",
            "quien eres",
            "preséntate",
            "presentate",
            "qué eres",
            "que eres",
            "qué puedes hacer",
            "que puedes hacer",
            "háblame de ti",
            "hablame de ti",
            "cómo te llamas",
            "como te llamas",
            "cuál es tu nombre",
            "cual es tu nombre",
        ]

        if any(trigger in lowered for trigger in presentation_triggers):
            return "PRESENTATION"

        # -------- MEMORY STORE --------
        if lowered.startswith("recuerda que") or lowered.startswith("recuerda"):
            return "STORE_MEMORY"

        # -------- MEMORY RECALL --------
        recall_triggers = [
            "qué recuerdas",
            "que recuerdas",
            "qué me gusta",
            "que me gusta",
            "mis gustos",
            "mis preferencias",
            "mi nombre",
            "recuerdas algo",
            "recuerda algo",
            "gustos",
        ]

        if any(trigger in lowered for trigger in recall_triggers):
            return "RECALL_MEMORY"

        # Patrones tipo: "qué música me gusta"
        if re.search(r"qué\s+.+\s+me\s+gusta", lowered) or \
           re.search(r"que\s+.+\s+me\s+gusta", lowered):
            return "RECALL_MEMORY"

        # -------- OPERATE (fallback por intent) --------
        operate_triggers = [
            "pon", "reproduce", "reproducir",
            "pausa", "pause", "pausar",
            "siguiente", "skip", "next",
            "continúa", "reanuda"
        ]

        if any(trigger in lowered for trigger in operate_triggers):
            return "OPERATE"

        # -------- TRELLO QUERIES --------
        trello_query_triggers = [
            "qué tengo hoy",
            "que tengo hoy",
            "pendientes de hoy",
            "pendientes hoy",
            "tareas de hoy",
            "qué tengo mañana",
            "que tengo mañana",
            "pendientes esta semana",
            "resumen del día",
            "resumen de hoy"
        ]

        if any(trigger in lowered for trigger in trello_query_triggers):
            return "TRELLO_QUERY"

        # -------- TRELLO ACTIONS --------
        trello_action_triggers = [
            "agregar tarea",
            "crear tarea",
            "nueva tarea",
            "recordatorio",
            "agregar recordatorio",
            "completar tarea",
            "marcar tarea",
            "marcar hábito",
            "completar hábito"
        ]

        if any(trigger in lowered for trigger in trello_action_triggers):
            return "TRELLO_ACTION"

        # -------- DEFAULT --------
        return "THINK"
