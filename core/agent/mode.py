from enum import Enum, auto

class AgentMode(Enum):
    CONVERSATION = auto()
    COMMAND = auto()
    THINK = auto()
