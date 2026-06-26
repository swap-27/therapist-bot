# session.py

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from database import db

# In-memory cache of active chat histories
store = {}


def get_session_history(session_id: int):

    # If this user's history is already in RAM,
    # don't reload it from SQLite.
    if session_id in store:
        return store[session_id]

    history = InMemoryChatMessageHistory()

    # Load previous messages from the database
    messages = db.load_messages(session_id)

    for message in messages:

        role = message["role"]
        content = message["content"]

        if role == "human":
            history.add_message(
                HumanMessage(content=content)
            )

        elif role == "ai":
            history.add_message(
                AIMessage(content=content)
            )

    store[session_id] = history

    return history