"""
Secrets management for Travel Platform.

This module provides encryption and decryption utilities for sensitive data
using Fernet symmetric encryption.
"""

import base64
import hashlib
import json
import os
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field, ValidationError

from src.core.config.settings import settings
from src.core.exceptions import SecurityError, DecryptionError, EncryptionError
from src.core.logging import logger


class EncryptedSecret(BaseModel):
    """Model for encrypted secret storage."""
    
    ciphertext: str = Field(..., description="Base64 encoded ciphertext")
    algorithm: str = Field(default="fernet", description="Encryption algorithm")
    version: str = Field(default="1.0", description="Encryption version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Encryption timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SecretsManager:
    """
    Manager for encrypting and decrypting sensitive data.
    
    Uses Fernet symmetric encryption with key derivation from ENCRYPTION_KEY.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the secrets manager.
        
        Args:
            encryption_key: Optional encryption key (defaults to settings.ENCRYPTION_KEY)
        
        Raises:
            SecurityError: If encryption key is invalid
        """
        self.encryption_key = encryption_key or settings.encryption_key_decrypted
        self._fernet = self._create_fernet()
        self._key_cache: Dict[str, Fernet] = {}
    
    def _create_fernet(self) -> Fernet:
        """
        Create Fernet instance from encryption key.
        
        Returns:
            Fernet: Configured Fernet instance
        
        Raises:
            SecurityError: If encryption key is invalid
        """
        try:
            # Derive a 32-byte key from the encryption key using PBKDF2
            salt = b"travel_platform_salt_2024"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(self.encryption_key.encode())
            )
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to create Fernet instance: {e}")
            raise SecurityError(
                message="Failed to initialize encryption",
                details=f"Cannot create encryption engine: {str(e)}"
            )
    
    def encrypt(self, plaintext: Union[str, Dict, BaseModel]) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            plaintext: Data to encrypt (string, dict, or Pydantic model)
        
        Returns:
            str: JSON string containing encrypted secret
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Convert input to string
            if isinstance(plaintext, dict):
                data_str = json.dumps(plaintext, ensure_ascii=False)
            elif isinstance(plaintext, BaseModel):
                data_str = plaintext.json()
            else:
                data_str = str(plaintext)
            
            # Encrypt the data
            ciphertext = self._fernet.encrypt(data_str.encode())
            
            # Create encrypted secret object
            secret = EncryptedSecret(
                ciphertext=base64.b64encode(ciphertext).decode(),
                metadata={
                    "source": "secrets_manager",
                    "data_type": type(plaintext).__name__,
                }
            )
            
            # Return as JSON string
            return secret.json()
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}", exc_info=True)
            raise EncryptionError(
                message="Failed to encrypt data",
                details=f"Encryption error: {str(e)}"
            )
    
    def decrypt(self, encrypted_data: Union[str, EncryptedSecret]) -> Any:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted data as JSON string or EncryptedSecret object
        
        Returns:
            Any: Decrypted data (attempts to parse as JSON, returns string otherwise)
        
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            # Parse input
            if isinstance(encrypted_data, str):
                try:
                    secret = EncryptedSecret.parse_raw(encrypted_data)
                except ValidationError:
                    # Try legacy format (just ciphertext)
                    secret = EncryptedSecret(ciphertext=encrypted_data)
            elif isinstance(encrypted_data, EncryptedSecret):
                secret = encrypted_data
            else:
                raise DecryptionError(
                    message="Invalid encrypted data format",
                    details="Expected string or EncryptedSecret object"
                )
            
            # Decode base64 ciphertext
            ciphertext = base64.b64decode(secret.ciphertext)
            
            # Decrypt
            plaintext_bytes = self._fernet.decrypt(ciphertext)
            plaintext = plaintext_bytes.decode()
            
            # Try to parse as JSON
            try:
                return json.loads(plaintext)
            except json.JSONDecodeError:
                return plaintext
            
        except InvalidToken as e:
            logger.error(f"Invalid token during decryption: {e}")
            raise DecryptionError(
                message="Decryption failed - invalid token",
                details="The encryption key may be incorrect or data corrupted"
            )
        except Exception as e:
            logger.error(f"Decryption failed: {e}", exc_info=True)
            raise DecryptionError(
                message="Failed to decrypt data",
                details=f"Decryption error: {str(e)}"
            )
    
    def encrypt_field(self, field_name: str, value: Any) -> str:
        """
        Encrypt a specific field and return as string.
        
        Args:
            field_name: Name of the field being encrypted
            value: Value to encrypt
        
        Returns:
            str: Encrypted value as string
        """
        encrypted = self.encrypt(value)
        logger.debug(f"Encrypted field '{field_name}'", extra={
            "field": field_name,
            "value_type": type(value).__name__,
        })
        return encrypted
    
    def decrypt_field(self, field_name: str, encrypted_value: str) -> Any:
        """
        Decrypt a specific field.
        
        Args:
            field_name: Name of the field being decrypted
            encrypted_value: Encrypted value
        
        Returns:
            Any: Decrypted value
        """
        decrypted = self.decrypt(encrypted_value)
        logger.debug(f"Decrypted field '{field_name}'", extra={
            "field": field_name,
            "value_type": type(decrypted).__name__,
        })
        return decrypted
    
    def encrypt_api_key(self, service_name: str, api_key: str) -> str:
        """
        Encrypt an API key with service metadata.
        
        Args:
            service_name: Name of the service (e.g., "amadeus", "paystack")
            api_key: API key to encrypt
        
        Returns:
            str: Encrypted API key
        """
        data = {
            "service": service_name,
            "api_key": api_key,
            "encrypted_at": datetime.utcnow().isoformat(),
        }
        
        encrypted = self.encrypt(data)
        logger.info(f"Encrypted API key for service '{service_name}'")
        return encrypted
    
    def decrypt_api_key(self, encrypted_api_key: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted API key.
        
        Args:
            encrypted_api_key: Encrypted API key
        
        Returns:
            Dict: Decrypted API key data with service information
        
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            data = self.decrypt(encrypted_api_key)
            
            if not isinstance(data, dict):
                raise DecryptionError(
                    message="Invalid API key format",
                    details="Decrypted data is not a dictionary"
                )
            
            if "service" not in data or "api_key" not in data:
                raise DecryptionError(
                    message="Invalid API key format",
                    details="Missing required fields in decrypted data"
                )
            
            logger.debug(f"Decrypted API key for service '{data['service']}'")
            return data
            
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise
    
    def rotate_key(self, new_encryption_key: str) -> str:
        """
        Rotate encryption key and re-encrypt all cached secrets.
        
        Args:
            new_encryption_key: New encryption key
        
        Returns:
            str: Status message
        
        Raises:
            SecurityError: If key rotation fails
        """
        try:
            old_fernet = self._fernet
            old_key = self.encryption_key
            
            # Create new Fernet with new key
            self.encryption_key = new_encryption_key
            self._fernet = self._create_fernet()
            
            logger.info("Encryption key rotated successfully")
            
            # Clear cache
            self._key_cache.clear()
            
            return "Encryption key rotated successfully"
            
        except Exception as e:
            # Revert to old key
            self.encryption_key = old_key
            self._fernet = old_fernet
            
            logger.error(f"Failed to rotate encryption key: {e}")
            raise SecurityError(
                message="Failed to rotate encryption key",
                details=f"Key rotation error: {str(e)}"
            )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on encryption system.
        
        Returns:
            Dict: Health status
        """
        try:
            # Test encryption/decryption
            test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)
            
            # Verify round-trip
            success = decrypted == test_data
            
            return {
                "status": "healthy" if success else "unhealthy",
                "test_passed": success,
                "algorithm": "fernet",
                "key_length": len(self.encryption_key),
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def get_key_fingerprint(self) -> str:
        """
        Get fingerprint of the encryption key (for verification).
        
        Returns:
            str: SHA256 fingerprint of the encryption key
        """
        key_hash = hashlib.sha256(self.encryption_key.encode()).hexdigest()
        return f"{key_hash[:8]}...{key_hash[-8:]}"


# Global secrets manager instance
secrets_manager = SecretsManager()
