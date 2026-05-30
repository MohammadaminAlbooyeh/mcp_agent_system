from agent.memory.short_term_memory import ShortTermMemory
from agent.memory.long_term_memory import LongTermMemory
from agent.memory.conversation_history import ConversationHistory
from agent.memory.context_window import ContextWindow
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.conversation = ConversationHistory()
        self.context = ContextWindow()

    def store(self, key: str, value: any, memory_type: str = "short_term"):
        if memory_type == "short_term":
            self.short_term.store(key, value)
        elif memory_type == "long_term":
            self.long_term.store(key, value)
        elif memory_type == "conversation":
            self.conversation.add(value)
        logger.debug(f"Stored in {memory_type}: {key}")

    def retrieve(self, key: str, memory_type: str = "short_term") -> any:
        if memory_type == "short_term":
            return self.short_term.retrieve(key)
        elif memory_type == "long_term":
            return self.long_term.retrieve(key)
        return None

    def clear_short_term(self):
        self.short_term.clear()
        logger.info("Short-term memory cleared")
