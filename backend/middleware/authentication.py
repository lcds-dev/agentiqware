"""
Authentication middleware
"""

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
import os
try:
    import jwt
except ImportError:
    # Fallback if PyJWT not installed
    jwt = None

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = None):
    """Verify JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        
        # Mock verification for development
        if token == "dummy_token":
            return {"user_id": "dummy_user_id", "email": "user@example.com"}
        
        # JWT verification if available
        if jwt and os.getenv("JWT_SECRET"):
            try:
                payload = jwt.decode(
                    token, 
                    os.getenv("JWT_SECRET"), 
                    algorithms=["HS256"]
                )
                return payload
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Default fallback for invalid tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )