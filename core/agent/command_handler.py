import re
from core.agent.context import AgentContext
from core.llm.gemini_client import GeminiClient
from core.planner.llama_planner import LlamaPlanner
from core.actions.action_registry import ActionRegistry


class CommandHandler:
    """Maneja la ejecución de comandos (THINK, OPERATE, PLAN)"""

    def __init__(
        self,
        context: AgentContext,
        thinker: GeminiClient,
        planner: LlamaPlanner,
        actions: ActionRegistry
    ):
        self.context = context
        self.thinker = thinker
        self.planner = planner
        self.actions = actions
        self.pending_action: dict | None = None

    def handle_follow_up(self, user_input: str) -> tuple[bool, str | None]:
        """
        Maneja follow-ups de acciones pendientes.
        
        Returns:
            tuple: (had_pending, response)
        """
        if not self.pending_action:
            return False, None

        pending = self.pending_action
        self.pending_action = None

        params = pending.get("params", {})
        params["query"] = user_input

        result = self.actions.execute({
            "action": pending.get("action"),
            "params": params
        })

        return True, result

    def handle_think(self, user_input: str) -> str:
        """Procesa con el modelo de pensamiento (Gemini)"""
        self.context.add("user", user_input)
        response = self.thinker.generate(self.context.get_context())
        self.context.add("assistant", response)
        return response

    def handle_operate(self, user_input: str) -> str:
        """Maneja comandos de operación (principalmente Spotify)"""
        lowered = user_input.lower()

        # Determinar comando
        if any(w in lowered for w in ("pausa", "pause", "pausar", "detén", "detener")):
            cmd = "pause"
        elif any(w in lowered for w in ("continúa", "continuar", "reanuda", "resume")):
            cmd = "play"
        elif any(w in lowered for w in ("siguiente", "next", "skip")):
            cmd = "next"
        else:
            cmd = "play"

        # Extraer query
        m = re.search(r"(?:pon|reproduce|reproducir|play)\s+(.*)", lowered)
        query = m.group(1).strip() if m else None

        # Ejecutar con query
        if query:
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {
                    "command": cmd,
                    "query": query
                }
            })

        # Comandos directos sin query
        if cmd in ("pause", "next"):
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {"command": cmd}
            })

        # Solicitar query
        self.pending_action = {
            "action": "SPOTIFY",
            "params": {"command": cmd}
        }
        return "¿Qué quieres escuchar?"

    def handle_plan(self, user_input: str) -> str:
        """Planifica y ejecuta acciones complejas"""
        self.context.add("user", user_input)
        plan = self.planner.plan(self.context.get_context())
        result = self.actions.execute(plan)
        self.context.add("assistant", result)
        return result