import json
from core.planner.base import Planner
from core.llm.llama_client import LlamaClient

SYSTEM_PROMPT = """
Eres un planner de acciones.
NO hablas con el usuario.
SIEMPRE respondes SOLO JSON válido.

Formato:
{
  "action": "NOMBRE_ACCION",
  "params": {}
}

Acciones disponibles:
- PLAY_SPOTIFY
- REMEMBER
- RECALL
- TALK

Si no hay acción clara, usa TALK.
"""

class LlamaPlanner(Planner):
    def __init__(self, llm: LlamaClient):
        self.llm = llm

    def plan(self, context: str) -> dict:
        raw = self.llm.generate(SYSTEM_PROMPT + "\n" + context)
        # Try direct JSON parse first
        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract a JSON object from the model output
            import re

            matches = re.findall(r"\{.*?\}", raw, re.S)
            plan = None
            if matches:
                # prefer the last JSON-like object in the output (model might echo the prompt)
                for candidate in reversed(matches):
                    try:
                        parsed = json.loads(candidate)
                    except json.JSONDecodeError:
                        continue
                    # ignore placeholder/template JSON from SYSTEM_PROMPT
                    action_val = parsed.get("action") if isinstance(parsed, dict) else None
                    if isinstance(action_val, str) and action_val.strip().upper() != "NOMBRE_ACCION":
                        plan = parsed
                        break
            else:
                plan = None

        if not plan or not isinstance(plan, dict):
            return {
                "action": "TALK",
                "params": {
                    "text": "No entendí qué acción ejecutar."
                }
            }

        # Normalize action names to registry names and add defaults
        action = plan.get("action", "TALK")
        params = plan.get("params", {}) or {}

        mapping = {
            "PLAY_SPOTIFY": ("SPOTIFY", {"command": "play"}),
            "PLAY-MUSIC": ("SPOTIFY", {"command": "play"}),
            "PLAY": ("SPOTIFY", {"command": "play"}),
            "PAUSE": ("SPOTIFY", {"command": "pause"}),
            "PAUSE_SPOTIFY": ("SPOTIFY", {"command": "pause"}),
            "NEXT": ("SPOTIFY", {"command": "next"}),
            "SPEAK": ("TALK", {}),
            "TALK": ("TALK", {}),
            "REMEMBER": ("TALK", {}),
            "RECALL": ("TALK", {}),
        }

        norm = action.strip().upper()
        if norm in mapping:
            mapped_action, default_params = mapping[norm]
            # merge provided params over defaults
            merged = {**default_params, **params}
            return {"action": mapped_action, "params": merged}

        # If action already matches registry (e.g., 'SPOTIFY') return as-is
        return {"action": action, "params": params}
