import os
import jwt
import datetime
from typing import Optional

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_secret_key_change_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived for magic link
SESSION_TOKEN_EXPIRE_DAYS = 90    # Long-lived for session

def create_magic_link_token(email: str) -> str:
    """Generates a short-lived JWT for the magic link."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "type": "magic_link", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_session_token(email: str) -> str:
    """Generates a long-lived JWT for the session cookie."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": email, "type": "session", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, expected_type: str) -> Optional[str]:
    """
    Verifies the JWT token and returns the email (sub) if valid.
    Checks for expiration and correct token type.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != expected_type:
            return None
            
        return email
    except jwt.PyJWTError:
        return None
