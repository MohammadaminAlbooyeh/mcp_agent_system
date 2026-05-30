import pytest
from agent.memory.conversation_history import ConversationHistory
from agent.memory.context_window import ContextWindow


def test_conversation_history():
    ch = ConversationHistory(max_length=3)
    ch.add({"role": "user", "content": "hello"})
    ch.add({"role": "assistant", "content": "hi"})
    assert len(ch) == 2
    ch.add({"role": "user", "content": "how are you?"})
    ch.add({"role": "assistant", "content": "good"})
    assert len(ch) == 3


def test_context_window():
    cw = ContextWindow(max_tokens=100)
    cw.add("test content", token_count=30)
    cw.add("more content", token_count=40)
    usage = cw.get_usage()
    assert usage["used"] == 70
    assert usage["max"] == 100
