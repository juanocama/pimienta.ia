from pathlib import Path
import re

from core.agent.context import AgentContext
from core.agent.router import IntentRouter

from core.llm.gemini_client import GeminiClient
from core.llm.llama_client import LlamaClient

from core.memory.sqlite_memory import SQLiteMemory
from core.memory.memory_service import MemoryService

from core.planner.llama_planner import LlamaPlanner

from core.actions.action_registry import ActionRegistry
from core.actions.spotify_action import SpotifyAction
from core.actions.talk import TalkAction

from core.personality.personality_service import PersonalityService
from core.personality.prompt_builder import build_personality_prompt


class Agent:
    def __init__(self):
        # ---------- CONTEXT ----------
        self.context = AgentContext()

        # ---------- ROUTER / THINKER ----------
        self.router = IntentRouter()
        self.thinker = GeminiClient()

        # ---------- MEMORY (BEFORE PERSONALITY) ----------
        self.memory = MemoryService(SQLiteMemory())

        # ---------- PERSONALITY ----------
        self.personality_service = PersonalityService(self.memory)
        self.personality = self.personality_service.load()

        # 👉 Personality prompt (SYSTEM)
        personality_prompt = build_personality_prompt(self.personality)
        self.context.add("system", personality_prompt)

        # ---------- ACTION REGISTRY ----------
        self.actions = ActionRegistry()
        self.actions.register("SPOTIFY", SpotifyAction())
        self.actions.register("TALK", TalkAction())

        # ---------- LLM OPERATOR ----------
        default_path = Path("models/mistral/mistral-7b-instruct.Q4_K_M.gguf")
        model_path = str(default_path)

        if not default_path.exists():
            mistral_dir = Path("models/mistral")
            if mistral_dir.exists():
                matches = list(mistral_dir.glob("mistral-7b-instruct*.gguf"))
                if matches:
                    model_path = str(matches[0])

        self.operator = LlamaClient(model_path=model_path)

        # ---------- PLANNER ----------
        self.planner = LlamaPlanner(self.operator)

        # ---------- FOLLOW-UP ----------
        self.pending_action: dict | None = None

    def handle(self, user_input: str) -> str:
        # ---------- FOLLOW-UP ----------
        if self.pending_action:
            pending = self.pending_action
            self.pending_action = None

            params = pending.get("params", {})
            params["query"] = user_input

            return self.actions.execute({
                "action": pending.get("action"),
                "params": params
            })

        # ---------- INTENT ----------
        intent = self.router.route(user_input)

        # ---------- MEMORY STORE ----------
        if intent == "STORE_MEMORY":
            fact = re.sub(
                r'^(recuerda\s+que|recuerda)\s*',
                '',
                user_input,
                flags=re.I
            ).strip()

            self.memory.remember(fact)
            return "Listo. Lo recordaré."

        # ---------- MEMORY RECALL ----------
        if intent == "RECALL_MEMORY":
            recalled = self.memory.recall(user_input)
            return (
                f"Esto es lo que recuerdo:\n{recalled}"
                if recalled else
                "No recuerdo nada relevante todavía."
            )

        # ---------- CONTEXT ----------
        self.context.add("user", user_input)

        # ---------- THINK ----------
        if intent == "THINK":
            response = self.thinker.generate(self.context.get_context())
            self.context.add("assistant", response)
            return response

        # ---------- OPERATE (FAST PATH) ----------
        if intent == "OPERATE":
            lowered = user_input.lower()

            if any(w in lowered for w in ("pausa", "pause", "pausar", "detén", "detener")):
                cmd = "pause"
            elif any(w in lowered for w in ("continúa", "continuar", "reanuda", "resume")):
                cmd = "play"
            elif any(w in lowered for w in ("siguiente", "next", "skip")):
                cmd = "next"
            else:
                cmd = "play"

            m = re.search(r"(?:pon|reproduce|reproducir|play)\s+(.*)", lowered)
            query = m.group(1).strip() if m else None

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

            self.pending_action = {
                "action": "SPOTIFY",
                "params": {"command": cmd}
            }
            return "¿Qué quieres escuchar?"

        # ---------- PLAN + EXECUTE ----------
        plan = self.planner.plan(self.context.get_context())
        result = self.actions.execute(plan)

        self.context.add("assistant", result)
        return result



