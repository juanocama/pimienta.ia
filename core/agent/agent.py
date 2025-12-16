from core.agent.context import AgentContext
from core.agent.router import IntentRouter
from core.llm.gemini_client import GeminiClient
from core.llm.llama_client import LlamaClient
from core.memory.sqlite_memory import SQLiteMemory
from core.memory.memory_service import MemoryService
from pathlib import Path

class Agent:
    def __init__(self):
        self.context = AgentContext()
        self.router = IntentRouter()

        self.thinker = GeminiClient()

        # Prefer explicit expected path, but try to auto-detect variants
        default_path = Path("models/mistral/mistral-7b-instruct.Q4_K_M.gguf")
        self.memory = MemoryService(SQLiteMemory())
        model_path = str(default_path)

        if not default_path.exists():
            mistral_dir = Path("models/mistral")
            if mistral_dir.exists():
                matches = list(mistral_dir.glob("mistral-7b-instruct*.gguf"))
                if matches:
                    model_path = str(matches[0])

        self.operator = LlamaClient(
            model_path=model_path
        )

    def handle(self, user_input: str) -> str:
        intent = self.router.route(user_input)

        if intent == "STORE_MEMORY":
            # remove leading phrases like 'recuerda que' or 'recuerda' (case-insensitive)
            import re

            fact = re.sub(r'^(recuerda\s+que|recuerda)\s*', '', user_input, flags=re.I).strip()
            # normalize leading phrases like 'me gusta ...'
            self.memory.remember(fact)
            return "Listo. Lo recordaré."

        if intent == "RECALL_MEMORY":
            # pass the full user query to recall so MemoryService can decide what to fetch
            recalled = self.memory.recall(user_input)
            if recalled:
                return f"Esto es lo que recuerdo:\n{recalled}"
            else:
                return "No recuerdo nada relevante todavía."

        self.context.add("User", user_input)

        if intent == "THINK":
            response = self.thinker.generate(self.context.get_context())
        else:
            response = self.operator.generate(self.context.get_context())

        self.context.add("Agent", response)
        return response


