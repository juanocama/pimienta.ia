class ActionRegistry:
    def __init__(self):
        self.actions = {}

    def register(self, name: str, action):
        self.actions[name] = action

    def execute(self, plan: dict) -> str:
        action_name = plan.get("action")
        params = plan.get("params", {})

        action = self.actions.get(action_name)

        if not action:
            return f"Acción no registrada: {action_name}"

        return action.execute(params)
