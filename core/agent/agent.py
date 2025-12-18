from pathlib import Path

from core.agent.context import AgentContext
from core.agent.router import IntentRouter
from core.agent.wake_handler import WakeHandler
from core.agent.memory_handler import MemoryHandler
from core.agent.command_handler import CommandHandler

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
    """Orquestador principal del agente conversacional"""

    def __init__(self):
        # ---------- CORE COMPONENTS ----------
        self.context = AgentContext()
        self.router = IntentRouter()
        self.thinker = GeminiClient()

        # ---------- MEMORY ----------
        self.memory = MemoryService(SQLiteMemory())

        # ---------- PERSONALITY ----------
        self.personality_service = PersonalityService(self.memory)
        self.personality = self.personality_service.load()
        
        personality_prompt = build_personality_prompt(self.personality)
        self.context.add("system", personality_prompt)

        # ---------- ACTIONS ----------
        self.actions = ActionRegistry()
        self.actions.register("SPOTIFY", SpotifyAction())
        self.actions.register("TALK", TalkAction())

        # ---------- LLM OPERATOR ----------
        self.operator = self._initialize_operator()

        # ---------- PLANNER ----------
        self.planner = LlamaPlanner(self.operator)

        # ---------- HANDLERS ----------
        self.wake_handler = WakeHandler()
        self.memory_handler = MemoryHandler(self.memory)
        self.command_handler = CommandHandler(
            self.context,
            self.thinker,
            self.planner,
            self.actions
        )

    def _initialize_operator(self) -> LlamaClient:
        """Inicializa el cliente LLM local"""
        default_path = Path("models/mistral/mistral-7b-instruct.Q4_K_M.gguf")
        model_path = str(default_path)

        if not default_path.exists():
            mistral_dir = Path("models/mistral")
            if mistral_dir.exists():
                matches = list(mistral_dir.glob("mistral-7b-instruct*.gguf"))
                if matches:
                    model_path = str(matches[0])

        return LlamaClient(model_path=model_path)

    def _get_presentation(self) -> str:
        """Devuelve la presentación del agente basada en su personalidad"""
        p = self.personality
        
        # Construcción de presentación personalizada
        intro = f"¡Hola! Soy {p.name}, tu asistente de ia con voz, tengo instruido ser directa y bromear"
        capabilities = []
        capabilities.append("Controlar tu música de Spotify")
        capabilities.append("Recordar tus gustos y preferencias")
        capabilities.append("Conversar contigo de forma natural")
        capabilities.append("Ayudarte con tareas y recordatorios")
        
        capabilities_text = "\n\n¿Qué puedo hacer?\n" + "\n".join(capabilities)
        
        wake_word_reminder = "\n\nDi 'pimienta' para activarme cuando estoy en modo pasivo 😴"
        
        return intro + capabilities_text + wake_word_reminder

    def handle(self, user_input: str) -> str:
        """
        Punto de entrada principal para procesar input del usuario.
        
        Args:
            user_input: Texto del usuario
            
        Returns:
            Respuesta del agente
        """
        # ---------- WAKE WORD ----------
        should_continue, processed_input, immediate_response = \
            self.wake_handler.process_input(user_input)

        if immediate_response:
            return immediate_response

        if not should_continue:
            return ""

        user_input = processed_input

        # ---------- FOLLOW-UP ----------
        had_pending, response = self.command_handler.handle_follow_up(user_input)
        if had_pending:
            self.wake_handler.refresh_window()
            return response

        # ---------- INTENT ROUTING ----------
        intent = self.router.route(user_input)

        # ---------- PRESENTATION ----------
        if intent == "PRESENTATION":
            response = self._get_presentation()
            self.wake_handler.refresh_window()
            return response

        # ---------- MEMORY OPERATIONS ----------
        if intent == "STORE_MEMORY":
            response = self.memory_handler.handle_store(user_input)
            self.wake_handler.refresh_window()
            return response

        if intent == "RECALL_MEMORY":
            response = self.memory_handler.handle_recall(user_input)
            self.wake_handler.refresh_window()
            return response

        # ---------- MUSIC PREFERENCES ----------
        is_preference, response = self.memory_handler.handle_music_preference(user_input)
        if is_preference:
            self.wake_handler.refresh_window()
            return response

        # ---------- COMMAND EXECUTION ----------
        if intent == "THINK":
            response = self.command_handler.handle_think(user_input)
            self.wake_handler.refresh_window()
            return response

        if intent == "OPERATE":
            response = self.command_handler.handle_operate(user_input)
            self.wake_handler.refresh_window()
            return response

        # ---------- PLAN & EXECUTE ----------
        response = self.command_handler.handle_plan(user_input)
        self.wake_handler.refresh_window()
        return response