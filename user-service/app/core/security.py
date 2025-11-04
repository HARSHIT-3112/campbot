from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import logging

# ----------------------------------------------------------------------
# Logger setup
# ----------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

# ----------------------------------------------------------------------
# JWT Token Creation & Validation
# ----------------------------------------------------------------------
def create_access_token(data: dict) -> str:
    """
    Create a short-lived JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token() -> str:
    """
    Create an opaque refresh token (64-byte random string).
    Stored server-side (DB) for security & rotation.
    """
    return secrets.token_urlsafe(64)


def decode_token(token: str):
    """
    Decode a JWT and return its payload.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT Decode Error: {e}")
        return None


def is_access_token(token_data: dict) -> bool:
    """
    Ensure the token type is 'access' to avoid misuse of refresh tokens.
    """
    return token_data and token_data.get("type") == "access"
