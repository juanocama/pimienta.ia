from core.agent.context import AgentContext
from core.agent.router import IntentRouter
from core.llm.gemini_client import GeminiClient
from core.llm.llama_client import LlamaClient
from pathlib import Path


class Agent:
    def __init__(self):
        self.context = AgentContext()
        self.router = IntentRouter()

        self.thinker = GeminiClient()

        # Prefer explicit expected path, but try to auto-detect variants
        default_path = Path("models/mistral/mistral-7b-instruct.Q4_K_M.gguf")
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
        self.context.add("User", user_input)
        intent = self.router.route(user_input)

        if intent == "THINK":
            prompt = (
                "Responde de forma clara y concisa.\n\n"
                + self.context.get_context()
            )
            response = self.thinker.generate(prompt)
        else:
            prompt = (
                "Eres un agente que estructura acciones.\n"
                "No expliques, solo indica qué acción realizar.\n\n"
                + self.context.get_context()
            )
            response = self.operator.generate(prompt)

        self.context.add("Agent", response)
        return response

