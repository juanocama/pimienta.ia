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

    # -------------------------------------------------
    # FOLLOW UPS
    # -------------------------------------------------
    def handle_follow_up(self, user_input: str) -> tuple[bool, str | None]:
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

    # -------------------------------------------------
    # THINK
    # -------------------------------------------------
    def handle_think(self, user_input: str) -> str:
        self.context.add("user", user_input)
        response = self.thinker.generate(self.context.get_context())
        self.context.add("assistant", response)
        return response

    # -------------------------------------------------
    # OPERATE (SPOTIFY)
    # -------------------------------------------------
    def handle_operate(self, user_input: str) -> str:
        lowered = user_input.lower().strip()

        # ---------- PASO 13: COMANDOS DIRECTOS DJ / LIKED ----------
        if any(p in lowered for p in (
            "música que me gusta",
            "musica que me gusta",
            "mis me gusta",
            "mis gustos musicales"
        )):
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {"command": "play_liked"}
            })

        if any(p in lowered for p in (
            "activa al dj",
            "activa el dj",
            "pon al dj",
            "modo dj"
        )):
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {"command": "play_dj"}
            })

        # ---------- COMANDOS CLÁSICOS ----------
        if any(w in lowered for w in ("pausa", "pause", "pausar", "detén", "detener")):
            cmd = "pause"
        elif any(w in lowered for w in ("continúa", "continuar", "reanuda", "resume")):
            cmd = "play"
        elif any(w in lowered for w in ("siguiente", "next", "skip")):
            cmd = "next"
        else:
            cmd = "play"

        # ---------- EXTRAER QUERY ----------
        m = re.search(r"(?:pon|reproduce|reproducir|play)\s+(.*)", lowered)
        query = m.group(1).strip() if m else None

        # ---------- EJECUTAR ----------
        if query:
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {
                    "command": cmd,
                    "query": query
                }
            })

        if cmd in ("pause", "next"):
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {"command": cmd}
            })

        # ---------- FOLLOW UP ----------
        self.pending_action = {
            "action": "SPOTIFY",
            "params": {"command": cmd}
        }
        return "¿Qué quieres escuchar?"

    # -------------------------------------------------
    # PLAN
    # -------------------------------------------------
    def handle_plan(self, user_input: str) -> str:
        self.context.add("user", user_input)
        plan = self.planner.plan(self.context.get_context())
        result = self.actions.execute(plan)
        self.context.add("assistant", result)
        return result
