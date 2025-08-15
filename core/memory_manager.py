from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableConfig

from config.settings import Settings

SESSION_ID = "ai_dev_pipeline"

chat_history = RedisChatMessageHistory(
    session_id=SESSION_ID,
    url=Settings.REDIS_URL,
)

memory = ConversationBufferMemory(
    chat_memory=chat_history,
    return_messages=True,
)

def get_runnable_config(agent_name: str) -> RunnableConfig:
    """Provides config for LLM chains with memory."""
    return RunnableConfig(configurable={
        "memory": memory,
        "session_id": SESSION_ID
    })

def save_memory(agent_name: str, message: str):
    """Persist message to memory store."""
    memory.save_context(
        {"input": agent_name},
        {"output": message}
    )

def retrieve_memory():
    """Retrieve all stored conversation messages."""
    return memory.load_memory_variables({})