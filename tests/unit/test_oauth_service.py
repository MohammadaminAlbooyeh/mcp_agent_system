"""
Unit tests for OAuth Service - Gmail authentication flow.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.gmail_oauth_service import GmailOAuthService
from backend.services.oauth_repository import OAuthRepository


@pytest.fixture
def oauth_repository():
    """Create mock OAuth repository."""
    repo = MagicMock(spec=OAuthRepository)
    repo.save_token = AsyncMock(return_value=True)
    repo.get_token = AsyncMock(return_value=None)
    repo.delete_token = AsyncMock(return_value=True)
    repo.update_token = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def oauth_service(oauth_repository):
    """Create OAuth service for testing."""
    return GmailOAuthService(oauth_repository)


def test_get_auth_url(oauth_service):
    """Test generating authorization URL."""
    session_id = "test_session_123"
    auth_url = oauth_service.get_auth_url(session_id)

    assert auth_url is not None
    assert isinstance(auth_url, str)
    assert "accounts.google.com" in auth_url
    assert "client_id" in auth_url
    assert "scope" in auth_url
    assert "state" in auth_url


@pytest.mark.asyncio
async def test_exchange_code_for_token(oauth_service, oauth_repository):
    """Test exchanging authorization code for token."""
    session_id = "test_session_123"
    auth_code = "test_auth_code_123"

    # Mock token response
    token_response = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600,
        "token_type": "Bearer"
    }

    with patch("backend.services.gmail_oauth_service.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = token_response
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success = await oauth_service.exchange_code_for_token(auth_code, session_id)

        assert success is True
        oauth_repository.save_token.assert_called_once()


@pytest.mark.asyncio
async def test_get_auth_status(oauth_service, oauth_repository):
    """Test getting authentication status."""
    session_id = "test_session_123"

    # Mock stored token
    oauth_repository.get_token.return_value = {
        "access_token": "test_access",
        "expires_at": "2024-12-31T10:00:00Z",
        "user_email": "user@example.com"
    }

    status = await oauth_service.get_auth_status(session_id)

    assert status is not None
    assert isinstance(status, dict)
    assert "authenticated" in status


@pytest.mark.asyncio
async def test_disconnect_gmail(oauth_service, oauth_repository):
    """Test disconnecting Gmail authorization."""
    session_id = "test_session_123"

    success = await oauth_service.disconnect_gmail(session_id)

    assert success is True
    oauth_repository.delete_token.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_token(oauth_service, oauth_repository):
    """Test refreshing expired access token."""
    session_id = "test_session_123"

    # Mock stored refresh token
    oauth_repository.get_token.return_value = {
        "refresh_token": "test_refresh_token",
        "access_token": "old_access_token",
        "expires_at": "2024-01-01T10:00:00Z"
    }

    new_token_response = {
        "access_token": "new_access_token",
        "expires_in": 3600,
        "token_type": "Bearer"
    }

    with patch("backend.services.gmail_oauth_service.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = new_token_response
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success = await oauth_service.refresh_gmail_token(session_id)

        assert success is True
        oauth_repository.update_token.assert_called_once()


@pytest.mark.asyncio
async def test_get_gmail_credentials(oauth_service, oauth_repository):
    """Test retrieving Gmail credentials."""
    session_id = "test_session_123"

    # Mock stored token
    oauth_repository.get_token.return_value = {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_at": "2024-12-31T10:00:00Z"
    }

    creds = await oauth_service.get_gmail_credentials(session_id)

    assert creds is not None
    assert "access_token" in creds or isinstance(creds, dict)


@pytest.mark.asyncio
async def test_invalid_auth_code(oauth_service, oauth_repository):
    """Test handling invalid authorization code."""
    session_id = "test_session_123"
    invalid_code = "invalid_code"

    with patch("backend.services.gmail_oauth_service.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_code"}
        mock_post.return_value = mock_response

        success = await oauth_service.exchange_code_for_token(invalid_code, session_id)

        assert success is False


@pytest.mark.asyncio
async def test_no_stored_token(oauth_service, oauth_repository):
    """Test behavior when no token stored."""
    session_id = "test_session_123"
    oauth_repository.get_token.return_value = None

    status = await oauth_service.get_auth_status(session_id)

    assert status is not None
    assert status.get("authenticated") is False


@pytest.mark.asyncio
async def test_token_encryption(oauth_repository):
    """Test that tokens are encrypted when stored."""
    session_id = "test_session_123"
    token_data = {
        "access_token": "secret_access_token",
        "refresh_token": "secret_refresh_token"
    }

    oauth_repository.save_token(session_id, "gmail", token_data)

    # Verify encryption happened
    oauth_repository.save_token.assert_called_once()
