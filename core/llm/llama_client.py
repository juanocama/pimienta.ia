from core.llm.base import LLMClient
from pathlib import Path
import os
import warnings

try:
    from llama_cpp import Llama  # type: ignore
    _HAVE_LLAMA = True
except Exception:
    _HAVE_LLAMA = False


class LlamaClient(LLMClient):
    def __init__(
        self,
        model_path: str | None = None,
        n_ctx: int = 2048,
        temperature: float = 0.3,
    ):
        # Allow override from environment variable MODEL_PATH
        env_model = os.getenv("MODEL_PATH")
        if env_model:
            model_path = env_model

        if model_path is None:
            warnings.warn("No model_path provided to LlamaClient; running in simulated mode.")
            self.available = False
            self.llm = None
            return

        model_file = Path(model_path)

        if not model_file.exists() or not _HAVE_LLAMA:
            warnings.warn(f"Modelo no encontrado o llama_cpp no disponible; falling back to simulated mode. Expected: {model_file.resolve()}")
            self.available = False
            self.llm = None
            return

        # Real model available
        self.available = True
        self.llm = Llama(
            model_path=str(model_file),
            n_ctx=n_ctx,
            temperature=temperature,
            verbose=False,
        )

    def generate(self, prompt: str) -> str:
        if not getattr(self, "available", False) or self.llm is None:
            # Simulated response when no local Llama binary/model is available
            return f"(simulado) respuesta a: {prompt}"

        output = self.llm(
            prompt,
            max_tokens=512,
            stop=["</s>"],
        )
        # llama-cpp-python may return choices differently depending on version
        try:
            return output["choices"][0]["text"].strip()
        except Exception:
            # fallback: try to stringify output
            return str(output)

