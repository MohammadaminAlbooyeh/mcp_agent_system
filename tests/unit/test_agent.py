import pytest
from agent.core.agent import Agent
from agent.memory.memory_manager import MemoryManager
from agent.memory.short_term_memory import ShortTermMemory


def test_agent_initialization():
    agent = Agent({"llm": "openai"})
    assert agent is not None


def test_memory_manager():
    mm = MemoryManager()
    mm.store("key1", "value1")
    assert mm.retrieve("key1") == "value1"


def test_short_term_memory():
    stm = ShortTermMemory()
    stm.store("test", "data")
    assert stm.retrieve("test") == "data"
    assert len(stm.get_all()) == 1
    stm.clear()
    assert len(stm.get_all()) == 0
