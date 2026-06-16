import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain password matches the hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hashes a plain text password using Bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

