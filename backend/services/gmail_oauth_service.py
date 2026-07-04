import os
from typing import Optional
from datetime import datetime, timedelta
from agent.utils.logger import get_logger
from backend.services.oauth_repository import OAuthRepository
import json
import base64

logger = get_logger(__name__)


class GmailOAuthService:
    def __init__(self, oauth_repository: OAuthRepository = None):
        self.repo = oauth_repository or OAuthRepository()
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/oauth/callback")

        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.service_account import Credentials as ServiceAccountCredentials
            from google.oauth2 import credentials
            self.google_auth = {
                "Request": Request,
                "ServiceAccountCredentials": ServiceAccountCredentials,
                "Credentials": credentials.Credentials,
            }
        except ImportError:
            logger.error("google-auth library not installed")
            self.google_auth = None

    def get_auth_url(self, session_id: str) -> str:
        if not self.client_id:
            raise ValueError("Google OAuth not configured")

        scopes = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
        ]

        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={'+'.join(scopes)}&"
            f"access_type=offline&"
            f"state={session_id}"
        )
        return auth_url

    async def exchange_code_for_token(self, code: str, session_id: str) -> bool:
        if not self.client_id or not self.client_secret:
            logger.error("OAuth not configured")
            return False

        try:
            import httpx

            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)

            if response.status_code != 200:
                logger.error(f"Failed to exchange code: {response.text}")
                return False

            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)

            token_expiry = datetime.now() + timedelta(seconds=expires_in)

            user_email = await self._get_user_email(access_token)

            scopes = token_data.get("scope", "").split()
            await self.repo.create(
                session_id=session_id,
                provider="gmail",
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry,
                scopes=scopes,
                user_email=user_email,
            )

            logger.info(f"Successfully exchanged OAuth code for {user_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to exchange OAuth code: {e}")
            return False

    async def get_gmail_credentials(self, session_id: str):
        token_model = await self.repo.get_by_session_and_provider(session_id, "gmail")

        if not token_model:
            logger.error(f"No Gmail OAuth token for session {session_id}")
            return None

        if token_model.is_expired():
            logger.info("Token expired, attempting refresh")
            success = await self.refresh_gmail_token(session_id)
            if not success:
                return None
            token_model = await self.repo.get_by_session_and_provider(session_id, "gmail")

        try:
            from google.oauth2.credentials import Credentials
            access_token = await self.repo.get_decrypted_access_token(token_model.id)
            refresh_token = await self.repo.get_decrypted_refresh_token(token_model.id)

            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
            )

            return credentials
        except Exception as e:
            logger.error(f"Failed to create credentials: {e}")
            return None

    async def refresh_gmail_token(self, session_id: str) -> bool:
        token_model = await self.repo.get_by_session_and_provider(session_id, "gmail")

        if not token_model or not token_model.refresh_token:
            logger.error("No refresh token available")
            return False

        try:
            import httpx

            refresh_token = await self.repo.get_decrypted_refresh_token(token_model.id)
            token_url = "https://oauth2.googleapis.com/token"

            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)

            if response.status_code != 200:
                logger.error(f"Failed to refresh token: {response.text}")
                return False

            token_data = response.json()
            new_access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            new_token_expiry = datetime.now() + timedelta(seconds=expires_in)

            await self.repo.update(
                token_model.id,
                access_token=new_access_token,
                token_expiry=new_token_expiry
            )

            logger.info(f"Successfully refreshed Gmail token for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False

    async def disconnect_gmail(self, session_id: str) -> bool:
        return await self.repo.revoke_by_session_and_provider(session_id, "gmail")

    async def is_authenticated(self, session_id: str) -> bool:
        token_model = await self.repo.get_by_session_and_provider(session_id, "gmail")
        if not token_model:
            return False

        if token_model.is_expired():
            success = await self.refresh_gmail_token(session_id)
            return success

        return True

    async def get_auth_status(self, session_id: str) -> dict:
        token_model = await self.repo.get_by_session_and_provider(session_id, "gmail")

        if not token_model:
            return {
                "authenticated": False,
                "user_email": None,
                "is_expired": None,
                "expires_at": None,
            }

        is_expired = token_model.is_expired()

        return {
            "authenticated": not is_expired,
            "user_email": token_model.user_email,
            "is_expired": is_expired,
            "expires_at": token_model.token_expiry.isoformat() if token_model.token_expiry else None,
        }

    async def _get_user_email(self, access_token: str) -> Optional[str]:
        try:
            import httpx

            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)

            if response.status_code == 200:
                user_info = response.json()
                return user_info.get("email")

            logger.warning(f"Failed to get user email: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user email: {e}")
            return None
