import re


class IntentRouter:
    def route(self, text: str) -> str:
        lowered = text.lower()

        if lowered.startswith("recuerda que"):
            return "STORE_MEMORY"

        # Broad recall detection: common phrases and patterns
        recall_triggers = [
            "que me gusta",
            "qué me gusta",
            "mis gustos",
            "recuerda",
            "mi nombre",
            "mis preferencias",
            "me gusta",
            "gustos",
        ]

        if any(trigger in lowered for trigger in recall_triggers):
            return "RECALL_MEMORY"

        # Also accept patterns like 'que <palabra> me gusta' (e.g. 'que musica me gusta')
        if re.search(r"que\s+.+\s+me\s+gusta", lowered) or re.search(r"qué\s+.+\s+me\s+gusta", lowered):
            return "RECALL_MEMORY"

        operate_triggers = ["pon", "reproduce", "abre", "enciende"]

        if any(trigger in lowered for trigger in operate_triggers):
            return "OPERATE"

        return "THINK"

