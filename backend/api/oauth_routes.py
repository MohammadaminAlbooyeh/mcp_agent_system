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
