import pytest
from backend.models.database import init_db


@pytest.fixture(autouse=True, scope="session")
def setup_database():
    init_db()


@pytest.fixture
def agent_config():
    return {
        "llm": "openai",
        "max_steps": 10,
        "max_context_tokens": 4000,
    }


@pytest.fixture
def mock_tool_result():
    return "Mock tool execution result"


@pytest.fixture
def sample_task():
    return "Test task description"
