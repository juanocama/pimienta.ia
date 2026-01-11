from pathlib import Path
import re

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
from core.actions.trello_action import TrelloAction

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
        self.actions.register("TRELLO", TrelloAction())

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

        intro = (
            f"¡Hola! Soy {p.name}, tu asistente de IA con voz. "
            "Soy directa, eficiente y con un toque de humor."
        )

        capabilities = [
            "Controlar tu música de Spotify",
            "Recordar tus gustos y preferencias",
            "Conversar contigo de forma natural",
            "Ayudarte con tareas y recordatorios",
        ]

        capabilities_text = "\n\n¿Qué puedo hacer?\n" + "\n".join(capabilities)
        wake_word_reminder = "\n\nDi 'pimienta' para activarme cuando estoy en modo pasivo 😴"

        return intro + capabilities_text + wake_word_reminder

    def handle(self, user_input: str) -> str:
        """
        Punto de entrada principal para procesar input del usuario.
        """
        # ---------- WAKE WORD ----------
        should_continue, processed_input, immediate_response = \
            self.wake_handler.process_input(user_input)

        if immediate_response:
            return immediate_response

        if not should_continue:
            return ""

        user_input = processed_input
        lowered = user_input.lower()

        # ---------- FOLLOW-UP ----------
        had_pending, response = self.command_handler.handle_follow_up(user_input)
        if had_pending:
            self.wake_handler.refresh_window()
            return response

        # ==========================================================
        # PASO 13 — INTERCEPTACIÓN DJ / MÚSICA QUE ME GUSTA (CLAVE)
        # ==========================================================
        if any(p in lowered for p in (
            "música que me gusta",
            "musica que me gusta",
            "mis me gusta",
            "mis gustos musicales"
        )):
            self.wake_handler.refresh_window()
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
            self.wake_handler.refresh_window()
            return self.actions.execute({
                "action": "SPOTIFY",
                "params": {"command": "play_dj"}
            })

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

        # ---------- TRELLO QUERIES ----------
        if intent == "TRELLO_QUERY":
            response = self._handle_trello_query(user_input)
            self.wake_handler.refresh_window()
            return response

        # ---------- TRELLO ACTIONS ----------
        if intent == "TRELLO_ACTION":
            response = self._handle_trello_action(user_input)
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

    # ----------------- TRELLO HELPERS -----------------
    def _handle_trello_query(self, user_input: str) -> str:
        lowered = user_input.lower()

        if "mañana" in lowered or "manana" in lowered:
            return self.actions.execute({
                "action": "TRELLO",
                "params": {"command": "summary_tomorrow"}
            })

        if "semana" in lowered:
            return self.actions.execute({
                "action": "TRELLO",
                "params": {"command": "summary_week"}
            })

        # Por defecto, devolver resumen del día
        return self.actions.execute({
            "action": "TRELLO",
            "params": {"command": "summary_today"}
        })

    def _handle_trello_action(self, user_input: str) -> str:
        lowered = user_input.lower()

        # Completar / marcar tarea
        if any(w in lowered for w in ("completar", "marcar", "terminar", "hecho")):
            task_name = self._extract_task_name(user_input)
            if not task_name:
                return "¿Qué tarea quieres completar?"

            return self.actions.execute({
                "action": "TRELLO",
                "params": {"command": "complete_task", "name": task_name}
            })

        # Agregar tarea -> iniciar flujo pendiente para pedir nombre/detalles
        if any(w in lowered for w in ("agregar", "crear", "nueva", "nuevo", "recordatorio")):
            # Guardar pending action para que CommandHandler reciba el follow-up
            self.command_handler.pending_action = {
                "action": "TRELLO",
                "params": {"command": "add_task"}
            }
            return "¿Qué tarea quieres agregar? Dime el nombre, y si quieres fecha o prioridad."

        # Hábitos
        if any(w in lowered for w in ("hábito", "habito", "marcar hábito", "marcar habito", "completar hábito")):
            habit_name = self._extract_task_name(user_input)
            if not habit_name:
                return "¿Qué hábito quieres marcar?"
            return self.actions.execute({
                "action": "TRELLO",
                "params": {"command": "mark_habit", "name": habit_name}
            })

        return "No entendí qué acción de Trello quieres hacer"

    def _extract_task_name(self, text: str) -> str:
        """Heurística simple para extraer el nombre de una tarea/hábito.

        Busca primero texto entre comillas, luego frases después de verbos comunes.
        """
        text = (text or "").strip()

        # 1) Texto entre comillas dobles o simples
        m = re.search(r'"([^"]+)"', text)
        if m:
            return m.group(1).strip()
        m = re.search(r"'([^']+)'", text)
        if m:
            return m.group(1).strip()

        # 2) Patrones con dos puntos o guión después del tipo/verb: "agregar tarea: comprar leche"
        m = re.search(r'(?:(?:agregar|crear|nueva|nuevo|añadir|add|recordatorio)\s+(?:tarea|recordatorio|evento)?\s*[:\-]\s*)(.+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 3) Verbos + posible tipo: "completar la tarea pagar factura", "marcar hábito leer 30 minutos"
        m = re.search(r'(?:completar|completa|completé|completado|marcar|marcado|terminar|terminé|hacer|hice|marqué)\s+(?:la\s+|el\s+)?(?:tarea|hábito|habito|evento)?\s*[:\-\s]*([\w\W]+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 4) Frases tipo "tarea comprar leche" o "habito leer 20 min"
        m = re.search(r'^(?:tarea|habito|hábito|evento)\s+[:\-\s]*([\w\W]+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 5) Preposiciones finales: 'para X' o 'de X' -> usar lo que sigue
        m = re.search(r'(?:para|de)\s+([\w\W]+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 6) Fallback: tomar todo lo que sigue al primer verbo de acción conocido
        m = re.search(r'(?:agregar|crear|completar|marcar|terminar|borrar|eliminar)\s+([\w\W]+)$', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        return ""
