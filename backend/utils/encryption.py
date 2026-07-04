import os
from cryptography.fernet import Fernet
from agent.utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionUtil:
    def __init__(self, key: str = None):
        self.key = key or os.getenv("ENCRYPTION_KEY")

        if not self.key:
            self.key = Fernet.generate_key().decode()
            logger.warning("No ENCRYPTION_KEY provided, using generated key. Please set ENCRYPTION_KEY env var for production")

        try:
            if isinstance(self.key, str):
                self.key = self.key.encode()
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self.cipher = None

    def encrypt(self, data: str) -> str:
        if not self.cipher:
            logger.warning("Encryption not available, returning plaintext")
            return data

        try:
            if isinstance(data, str):
                data = data.encode()
            encrypted = self.cipher.encrypt(data)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data

    def decrypt(self, encrypted_data: str) -> str:
        if not self.cipher:
            logger.warning("Decryption not available, returning as-is")
            return encrypted_data

        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()
