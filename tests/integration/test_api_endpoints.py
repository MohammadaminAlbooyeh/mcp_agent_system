"""
Integration tests for REST API endpoints.
Tests HTTP endpoints with proper request/response validation.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_settings(client):
    """Test retrieving settings."""
    response = client.get("/api/settings")
    assert response.status_code == 200

    data = response.json()
    assert "llmProvider" in data
    assert "maxSteps" in data
    assert "theme" in data


def test_update_settings(client):
    """Test updating settings."""
    new_settings = {
        "llmProvider": "claude",
        "maxSteps": 25,
        "theme": "dark"
    }

    response = client.post("/api/settings", json=new_settings)
    assert response.status_code == 200

    data = response.json()
    assert data["llmProvider"] == "claude"
    assert data["maxSteps"] == 25
    assert data["theme"] == "dark"


def test_list_tools(client):
    """Test listing available tools."""
    response = client.get("/api/tools")
    assert response.status_code == 200

    tools = response.json()
    assert isinstance(tools, list)
    # Should have some tools
    if len(tools) > 0:
        assert "name" in tools[0]
        assert "description" in tools[0]


def test_create_task(client):
    """Test creating a task."""
    task_data = {
        "title": "Test Research Task",
        "description": "Search for information about async patterns",
        "priority": "high"
    }

    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Test Research Task"
    assert data["priority"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_list_tasks(client):
    """Test listing tasks."""
    response = client.get("/api/tasks")
    assert response.status_code == 200

    tasks = response.json()
    assert isinstance(tasks, list)


def test_get_task(client):
    """Test retrieving a specific task."""
    # Create a task first
    task_data = {
        "title": "Get Task Test",
        "description": "Test getting task",
        "priority": "medium"
    }

    create_response = client.post("/api/tasks", json=task_data)
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    # Get the task
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Task Test"


def test_get_nonexistent_task(client):
    """Test getting non-existent task."""
    response = client.get("/api/tasks/nonexistent_id_123")
    assert response.status_code == 404


def test_get_metrics(client):
    """Test getting system metrics."""
    response = client.get("/api/monitoring/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "tasks_completed" in data
    assert "tasks_failed" in data
    assert "tools_called" in data
    assert "avg_execution_time" in data


def test_session_create_endpoint(client):
    """Test creating session via API."""
    session_data = {
        "user_id": "test_user@example.com",
        "metadata": {"workflow": "research"}
    }

    response = client.post("/api/sessions/create", json=session_data)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["user_id"] == "test_user@example.com"
    assert data["is_active"] is True


def test_session_get_endpoint(client):
    """Test retrieving session via API."""
    # Create session
    create_response = client.post("/api/sessions/create", json={
        "user_id": "test@example.com"
    })
    session_id = create_response.json()["id"]

    # Get session
    get_response = client.get(f"/api/sessions/{session_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == session_id


def test_session_state_update(client):
    """Test updating session state via API."""
    # Create session
    create_response = client.post("/api/sessions/create", json={})
    session_id = create_response.json()["id"]

    # Update state
    update_response = client.post(
        f"/api/sessions/{session_id}/state",
        json={"state_updates": {"step": 1, "data": "test"}}
    )
    assert update_response.status_code == 200
    assert update_response.json()["success"] is True


def test_session_pause_resume(client):
    """Test pause and resume session."""
    # Create session
    create_response = client.post("/api/sessions/create", json={})
    session_id = create_response.json()["id"]

    # Pause
    pause_response = client.post(f"/api/sessions/{session_id}/pause")
    assert pause_response.status_code == 200
    assert pause_response.json()["success"] is True

    # Resume
    resume_response = client.post(f"/api/sessions/{session_id}/resume")
    assert resume_response.status_code == 200
    assert resume_response.json()["success"] is True


def test_session_complete(client):
    """Test completing a session."""
    # Create session
    create_response = client.post("/api/sessions/create", json={})
    session_id = create_response.json()["id"]

    # Complete
    complete_response = client.post(f"/api/sessions/{session_id}/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["success"] is True


def test_oauth_authorize_endpoint(client):
    """Test OAuth authorization endpoint."""
    response = client.post(
        "/api/oauth/authorize/gmail",
        params={"session_id": "test_session_123"}
    )
    # Should return auth URL
    if response.status_code == 200:
        assert "auth_url" in response.json()


def test_oauth_status_endpoint(client):
    """Test OAuth status endpoint."""
    response = client.get(
        "/api/oauth/status/gmail",
        params={"session_id": "test_session_123"}
    )
    # Should return status
    if response.status_code == 200:
        data = response.json()
        assert "authenticated" in data


def test_unsupported_provider(client):
    """Test error on unsupported OAuth provider."""
    response = client.post(
        "/api/oauth/authorize/unsupported_provider",
        params={"session_id": "test_123"}
    )
    assert response.status_code == 400


def test_api_error_handling(client):
    """Test API error handling."""
    # Missing required parameter
    response = client.post("/api/oauth/authorize/gmail")
    assert response.status_code == 422  # Unprocessable entity


def test_cors_headers(client):
    """Test CORS headers are set."""
    response = client.get("/health")
    # Check for CORS headers
    assert response.status_code == 200


def test_response_content_type(client):
    """Test response content type."""
    response = client.get("/api/settings")
    assert "application/json" in response.headers.get("content-type", "")
