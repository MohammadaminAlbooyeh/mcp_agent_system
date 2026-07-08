from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from backend.services.gmail_oauth_service import GmailOAuthService
from backend.services.oauth_repository import OAuthRepository
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/oauth", tags=["oauth"])

_gmail_oauth_service = None
_oauth_repository = None


def get_gmail_oauth_service() -> GmailOAuthService:
    global _gmail_oauth_service
    if _gmail_oauth_service is None:
        _oauth_repository = OAuthRepository()
        _gmail_oauth_service = GmailOAuthService(_oauth_repository)
    return _gmail_oauth_service


class AuthorizeRequest(BaseModel):
    session_id: str
    provider: str = "gmail"


class CallbackRequest(BaseModel):
    code: str
    session_id: str
    provider: str = "gmail"


class AuthStatusResponse(BaseModel):
    authenticated: bool
    user_email: Optional[str]
    is_expired: Optional[bool]
    expires_at: Optional[str]


@router.post("/authorize/{provider}")
async def authorize(
    provider: str,
    session_id: str = Query(...),
    gmail_service: GmailOAuthService = Depends(get_gmail_oauth_service),
) -> dict:
    """
    Get OAuth authorization URL for provider.

    Initiates OAuth 2.0 flow by returning an authorization URL that user
    should visit in their browser to grant permission.

    Args:
        provider (str): OAuth provider (currently: "gmail")
        session_id (str): Session identifier for token storage

    Returns:
        dict: Authorization URL to redirect user to

    Example Response:
        ```json
        {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
            "provider": "gmail"
        }
        ```

    Supported Providers:
    - gmail: Google Gmail API access
    """
    try:
        if provider != "gmail":
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")

        auth_url = gmail_service.get_auth_url(session_id)
        return {"auth_url": auth_url, "provider": provider}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback/{provider}")
async def callback(
    provider: str,
    request: CallbackRequest,
    gmail_service: GmailOAuthService = Depends(get_gmail_oauth_service),
) -> dict:
    """
    Handle OAuth callback and exchange authorization code for access token.

    Called by OAuth provider after user grants permission. Exchanges the
    authorization code for an access token and refresh token. Tokens are
    encrypted and stored per session.

    Args:
        provider (str): OAuth provider (currently: "gmail")
        request (CallbackRequest): Contains authorization code and session_id

    Returns:
        dict: Success confirmation with user email

    Example Request:
        ```json
        {
            "code": "4/0AX4XfWh...",
            "session_id": "sess_123...",
            "provider": "gmail"
        }
        ```

    Token Storage:
    - Encrypted with ENCRYPTION_KEY from environment
    - Stored in database per session
    - Auto-refreshed when expired
    """
    try:
        if provider != "gmail":
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")

        success = await gmail_service.exchange_code_for_token(request.code, request.session_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code for token")

        status = await gmail_service.get_auth_status(request.session_id)
        return {
            "success": True,
            "provider": provider,
            "user_email": status.get("user_email"),
            "message": f"Successfully authenticated with {provider}",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{provider}", response_model=AuthStatusResponse)
async def get_status(
    provider: str,
    session_id: str = Query(...),
    gmail_service: GmailOAuthService = Depends(get_gmail_oauth_service),
) -> AuthStatusResponse:
    """
    Check OAuth authentication status for a provider.

    Returns authentication status including whether token is valid and
    when it expires. Useful for UI to show auth state and refresh buttons.

    Args:
        provider (str): OAuth provider (currently: "gmail")
        session_id (str): Session identifier

    Returns:
        AuthStatusResponse: Authentication status with expiry info

    Example Response:
        ```json
        {
            "authenticated": true,
            "user_email": "user@example.com",
            "is_expired": false,
            "expires_at": "2024-01-15T10:30:00Z"
        }
        ```
    """
    try:
        if provider != "gmail":
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")

        status = await gmail_service.get_auth_status(session_id)
        return AuthStatusResponse(
            authenticated=status.get("authenticated", False),
            user_email=status.get("user_email"),
            is_expired=status.get("is_expired"),
            expires_at=status.get("expires_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect/{provider}")
async def disconnect(
    provider: str,
    session_id: str = Query(...),
    gmail_service: GmailOAuthService = Depends(get_gmail_oauth_service),
) -> dict:
    """
    Revoke OAuth credentials and disconnect from provider.

    Removes stored access token and refresh token for this session.
    User will need to re-authenticate to use provider features again.

    Args:
        provider (str): OAuth provider (currently: "gmail")
        session_id (str): Session identifier

    Returns:
        dict: Success confirmation
    """
    try:
        if provider != "gmail":
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")

        success = await gmail_service.disconnect_gmail(session_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to disconnect provider")

        return {"success": True, "message": f"Disconnected from {provider}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh/{provider}")
async def refresh_token(
    provider: str,
    session_id: str = Query(...),
    gmail_service: GmailOAuthService = Depends(get_gmail_oauth_service),
) -> dict:
    """
    Manually refresh OAuth access token.

    Exchanges refresh token for new access token. Usually called automatically
    when token expires, but can be called manually to ensure fresh token.

    Args:
        provider (str): OAuth provider (currently: "gmail")
        session_id (str): Session identifier

    Returns:
        dict: Success confirmation with refresh status
    """
    try:
        if provider != "gmail":
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")

        success = await gmail_service.refresh_gmail_token(session_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to refresh token")

        return {"success": True, "message": f"Token refreshed for {provider}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
