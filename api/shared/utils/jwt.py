from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data (Dict[str, Any]): Token data
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        data (Dict[str, Any]): Token data
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token (str): JWT token
        
    Returns:
        Dict[str, Any]: Token data
        
    Raises:
        JWTError: If token is invalid
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def is_token_valid(token: str) -> bool:
    """
    Check if a JWT token is valid.
    
    Args:
        token (str): JWT token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        decode_token(token)
        return True
    except JWTError:
        return False


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get token expiration time.
    
    Args:
        token (str): JWT token
        
    Returns:
        datetime: Token expiration time
        
    Raises:
        JWTError: If token is invalid
    """
    payload = decode_token(token)
    exp = payload.get("exp")
    
    if exp:
        return datetime.fromtimestamp(exp)
    
    return None