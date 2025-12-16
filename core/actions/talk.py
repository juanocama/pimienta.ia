from core.actions.base_action import Action

class TalkAction(Action):
    def execute(self, params: dict) -> str:
        return params.get("text", "")
