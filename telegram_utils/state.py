from enum import Enum

chat_states = {}


class State(Enum):
    NONE = "none"
    BUSSTOP = "busstop"


def set_state(chat_id: str, state: State):
    chat_states[chat_id] = state


def get_state(chat_id: str) -> State:
    if chat_id in chat_states:
        return chat_states[chat_id]
    else:
        return State.NONE


def clear_state(chat_id: str):
    chat_states.pop(chat_id, None)
