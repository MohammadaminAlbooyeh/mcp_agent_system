from agent.llm.openai_llm import OpenAILLM
from agent.llm.claude_llm import ClaudeLLM
from agent.llm.groq_llm import GroqLLM
from agent.llm.local_llm import LocalLLM
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class LLMFactory:
    @staticmethod
    def create(provider: str = "openai", config: dict = None):
        providers = {
            "openai": OpenAILLM,
            "claude": ClaudeLLM,
            "groq": GroqLLM,
            "local": LocalLLM,
        }
        cls = providers.get(provider)
        if not cls:
            logger.warning(f"Unknown provider '{provider}', falling back to OpenAI")
            cls = OpenAILLM
        return cls(config or {})
