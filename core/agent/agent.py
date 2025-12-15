from core.agent.context import AgentContext
from core.agent.router import IntentRouter
from core.llm.gemini_client import GeminiClient

class Agent:
    def __init__(self):
        self.context = AgentContext()
        self.router = IntentRouter()
        self.thinker = GeminiClient()

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
            response = "⚙️ Acción detectada (aún no implementada)"

        self.context.add("Agent", response)
        return response
