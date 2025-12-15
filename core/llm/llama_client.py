from core.llm.base import LLMClient
from llama_cpp import Llama
from pathlib import Path

class LlamaClient(LLMClient):
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        temperature: float = 0.3
    ):
        model_file = Path(model_path)

        if not model_file.exists():
            raise FileNotFoundError(
                f"Modelo no encontrado en: {model_file.resolve()}"
            )

        self.llm = Llama(
            model_path=str(model_file),
            n_ctx=n_ctx,
            temperature=temperature,
            verbose=False
        )

    def generate(self, prompt: str) -> str:
        output = self.llm(
            prompt,
            max_tokens=512,
            stop=["</s>"]
        )
        return output["choices"][0]["text"].strip()
