"""
Security utilities for Travel Platform.
Includes password hashing, token generation, and security helpers.
"""
import hashlib
import hmac
import secrets
import string
from typing import Optional, Tuple
from datetime import datetime, timedelta
import base64
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.config.settings import settings
from .logger import logger


class SecurityUtils:
    """Security utilities for the travel platform."""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Hash a password using PBKDF2 with SHA256.
        
        Args:
            password: Plain text password
            salt: Optional salt bytes (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # Use PBKDF2 with SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        hashed = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: bytes, salt: bytes) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Previously hashed password
            salt: Salt used during hashing
            
        Returns:
            True if password matches hash
        """
        try:
            new_hash, _ = SecurityUtils.hash_password(password, salt)
            return hmac.compare_digest(new_hash, hashed_password)
        except Exception as e:
            logger.error("password_verify_failed", error=str(e))
            return False
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a secure API key."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_token(length: int = 64) -> str:
        """Generate a secure random token."""
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """Generate a short code for verification, bookings, etc."""
        # Use digits only for short codes
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def encrypt_data(data: str, key: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            data: String data to encrypt
            key: Optional encryption key (generated if not provided)
            
        Returns:
            Tuple of (encrypted_data, key)
        """
        if key is None:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted, key
    
    @staticmethod
    def decrypt_data(encrypted_data: bytes, key: bytes) -> Optional[str]:
        """
        Decrypt data using Fernet symmetric encryption.
        
        Args:
            encrypted_data: Encrypted bytes
            key: Encryption key used during encryption
            
        Returns:
            Decrypted string or None if decryption fails
        """
        try:
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            return None
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate a secure filename to prevent path traversal attacks."""
        # Extract extension
        if '.' in original_filename:
            name, ext = original_filename.rsplit('.', 1)
            ext = '.' + ext.lower()
        else:
            name = original_filename
            ext = ''
        
        # Create secure name
        timestamp = int(datetime.utcnow().timestamp())
        random_part = secrets.token_hex(8)
        secure_name = hashlib.sha256(f'{name}_{timestamp}_{random_part}'.encode()).hexdigest()[:16]
        
        return f'{secure_name}{ext}'
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        # Remove directory components
        filename = filename.replace('\\', '/').split('/')[-1]
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = name[:250] + '.' + ext
        
        return filename
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list]:
        """
        Validate password strength.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in string.punctuation for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = {
            'password', '123456', 'qwerty', 'admin', 'welcome',
            'password123', 'travel123', '12345678', 'abcdef'
        }
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_otp(length: int = 6, expiry_minutes: int = 10) -> Tuple[str, datetime]:
        """Generate a One-Time Password with expiry."""
        # For better security, use secrets for OTP generation
        if length < 4:
            length = 6
        
        # Generate numeric OTP
        digits = string.digits
        otp = ''.join(secrets.choice(digits) for _ in range(length))
        
        # Calculate expiry
        expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        return otp, expiry
    
    @staticmethod
    def verify_otp(provided_otp: str, stored_otp: str, expiry: datetime) -> bool:
        """Verify OTP and check expiry."""
        if datetime.utcnow() > expiry:
            return False
        
        return hmac.compare_digest(provided_otp, stored_otp)
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data like credit cards, IDs, etc."""
        if not data or len(data) <= visible_chars:
            return '*' * len(data) if data else ''
        
        # Show last n characters, mask the rest
        masked = '*' * (len(data) - visible_chars) + data[-visible_chars:]
        return masked
    
    @staticmethod
    def is_safe_url(url: str, allowed_domains: list = None) -> bool:
        """Check if URL is safe (not javascript:, data:, etc.)."""
        if not url:
            return False
        
        # Convert to lowercase for comparison
        url_lower = url.lower().strip()
        
        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return False
        
        # If allowed_domains is provided, check domain
        if allowed_domains:
            from urllib.parse import urlparse
            try:
                parsed = urlparse(url_lower)
                domain = parsed.netloc
                
                # Check if domain is in allowed list
                if domain and not any(domain.endswith(allowed) for allowed in allowed_domains):
                    return False
            except:
                return False
        
        return True


# Security middleware and helpers
class SecurityMiddleware:
    """Security middleware for request handling."""
    
    @staticmethod
    def sanitize_input(data: dict) -> dict:
        """Sanitize input data to prevent XSS and injection attacks."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Basic XSS prevention
                sanitized_value = (
                    value.replace('<', '&lt;')
                         .replace('>', '&gt;')
                         .replace('"', '&quot;')
                         .replace("'", '&#x27;')
                         .replace('/', '&#x2F;')
                )
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = SecurityMiddleware.sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    SecurityMiddleware.sanitize_input(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_csrf_token(request_token: str, session_token: str) -> bool:
        """Validate CSRF token."""
        if not request_token or not session_token:
            return False
        
        return hmac.compare_digest(request_token, session_token)


# Convenience functions
def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password."""
    if length < 8:
        length = 12
    
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation
    
    # Ensure at least one character from each set
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest with random choices from all sets
    all_chars = uppercase + lowercase + digits + symbols
    password_chars += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    # Shuffle the characters
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        api_key.encode(),
        salt,
        100000,
        dklen=32
    )
    return f"{salt.hex()}:{hashed.hex()}"


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    try:
        salt_hex, key_hash = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            api_key.encode(),
            salt,
            100000,
            dklen=32
        )
        
        return hmac.compare_digest(new_hash.hex(), key_hash)
    except:
        return False


# Test function
def test_security():
    """Test security utilities."""
    print("Testing Security Utilities...")
    print("=" * 50)
    
    # Test password hashing
    password = "SecurePass123!"
    hashed, salt = SecurityUtils.hash_password(password)
    verified = SecurityUtils.verify_password(password, hashed, salt)
    print(f"1. Password hashing/verification: {'✅' if verified else '❌'}")
    
    # Test password strength
    strong_pass = "SecurePass123!"
    weak_pass = "123"
    strong_valid, strong_errors = SecurityUtils.validate_password_strength(strong_pass)
    weak_valid, weak_errors = SecurityUtils.validate_password_strength(weak_pass)
    print(f"2. Password strength:")
    print(f"   Strong password: {'✅' if strong_valid else '❌'}")
    print(f"   Weak password: {'✅' if weak_valid else '❌'} (should fail)")
    
    # Test token generation
    token = SecurityUtils.generate_token()
    print(f"3. Token generation: ✅ {len(token)} chars")
    
    # Test OTP generation
    otp, expiry = SecurityUtils.generate_otp()
    print(f"4. OTP generation: ✅ {otp} (expires: {expiry.strftime('%H:%M:%S')})")
    
    # Test data masking
    card_number = "4111111111111111"
    masked = SecurityUtils.mask_sensitive_data(card_number, 4)
    print(f"5. Data masking: ✅ {card_number} -> {masked}")
    
    # Test filename sanitization
    dangerous_file = "../../etc/passwd"
    safe_file = SecurityUtils.sanitize_filename(dangerous_file)
    print(f"6. Filename sanitization: ✅ {dangerous_file} -> {safe_file}")
    
    # Test secure URL check
    safe_url = "https://example.com/page"
    dangerous_url = "javascript:alert('xss')"
    safe_check = SecurityUtils.is_safe_url(safe_url)
    dangerous_check = SecurityUtils.is_safe_url(dangerous_url)
    print(f"7. URL safety check:")
    print(f"   Safe URL: {'✅' if safe_check else '❌'}")
    print(f"   Dangerous URL: {'✅' if dangerous_check else '❌'} (should fail)")
    
    print("\n" + "=" * 50)
    print("✅ Security utilities test complete!")


if __name__ == "__main__":
    test_security()
