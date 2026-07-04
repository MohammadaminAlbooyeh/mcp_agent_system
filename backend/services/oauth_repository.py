from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.models.oauth_token import OAuthTokenModel
from backend.models.database import get_session
from backend.utils.encryption import EncryptionUtil
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class OAuthRepository:
    def __init__(self, encryption_key: str = None):
        self.encryption = EncryptionUtil(encryption_key)

    async def create(self, session_id: str, provider: str, access_token: str, refresh_token: str = None, token_expiry: datetime = None, scopes: List[str] = None, user_email: str = None) -> OAuthTokenModel:
        db = get_session()
        try:
            token = OAuthTokenModel(
                session_id=session_id,
                provider=provider,
                access_token=self.encryption.encrypt(access_token),
                refresh_token=self.encryption.encrypt(refresh_token) if refresh_token else None,
                token_expiry=token_expiry,
                scopes=scopes or [],
                user_email=user_email,
                is_active=True,
            )
            db.add(token)
            db.commit()
            db.refresh(token)
            logger.info(f"Created OAuth token for {provider} in session {session_id}")
            return token
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create OAuth token: {e}")
            raise
        finally:
            db.close()

    async def get_by_session_and_provider(self, session_id: str, provider: str) -> Optional[OAuthTokenModel]:
        db = get_session()
        try:
            token = db.query(OAuthTokenModel).filter(
                OAuthTokenModel.session_id == session_id,
                OAuthTokenModel.provider == provider,
                OAuthTokenModel.is_active == True
            ).first()
            return token
        except Exception as e:
            logger.error(f"Failed to get OAuth token: {e}")
            return None
        finally:
            db.close()

    async def update(self, token_id: str, access_token: str = None, refresh_token: str = None, token_expiry: datetime = None) -> bool:
        db = get_session()
        try:
            token = db.query(OAuthTokenModel).filter(OAuthTokenModel.id == token_id).first()
            if not token:
                return False

            if access_token:
                token.access_token = self.encryption.encrypt(access_token)
            if refresh_token is not None:
                token.refresh_token = self.encryption.encrypt(refresh_token) if refresh_token else None
            if token_expiry:
                token.token_expiry = token_expiry

            token.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update OAuth token: {e}")
            return False
        finally:
            db.close()

    async def delete(self, token_id: str) -> bool:
        db = get_session()
        try:
            token = db.query(OAuthTokenModel).filter(OAuthTokenModel.id == token_id).first()
            if token:
                token.is_active = False
                token.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete OAuth token: {e}")
            return False
        finally:
            db.close()

    async def revoke_by_session_and_provider(self, session_id: str, provider: str) -> bool:
        db = get_session()
        try:
            tokens = db.query(OAuthTokenModel).filter(
                OAuthTokenModel.session_id == session_id,
                OAuthTokenModel.provider == provider,
            ).all()

            for token in tokens:
                token.is_active = False
                token.updated_at = datetime.now()

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to revoke OAuth tokens: {e}")
            return False
        finally:
            db.close()

    async def get_decrypted_access_token(self, token_id: str) -> Optional[str]:
        db = get_session()
        try:
            token = db.query(OAuthTokenModel).filter(OAuthTokenModel.id == token_id).first()
            if token:
                return self.encryption.decrypt(token.access_token)
            return None
        except Exception as e:
            logger.error(f"Failed to get decrypted token: {e}")
            return None
        finally:
            db.close()

    async def get_decrypted_refresh_token(self, token_id: str) -> Optional[str]:
        db = get_session()
        try:
            token = db.query(OAuthTokenModel).filter(OAuthTokenModel.id == token_id).first()
            if token and token.refresh_token:
                return self.encryption.decrypt(token.refresh_token)
            return None
        except Exception as e:
            logger.error(f"Failed to get decrypted refresh token: {e}")
            return None
        finally:
            db.close()

    async def list_by_session(self, session_id: str) -> List[OAuthTokenModel]:
        db = get_session()
        try:
            return db.query(OAuthTokenModel).filter(
                OAuthTokenModel.session_id == session_id
            ).all()
        except Exception as e:
            logger.error(f"Failed to list OAuth tokens: {e}")
            return []
        finally:
            db.close()
