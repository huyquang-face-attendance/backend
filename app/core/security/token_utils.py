from datetime import timedelta
from typing import Optional, List
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import get_settings

settings = get_settings()


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=4
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(data: dict) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    expire = settings.datetime_now + \
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})

    if "roles" in data:
        to_encode["roles"] = data["roles"]
    if "permissions" in data:
        to_encode["permissions"] = data["permissions"]

    return jwt.encode(to_encode, settings.CLIENT_SECRET,
                      algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a new refresh token"""
    to_encode = data.copy()
    expire = settings.datetime_now + \
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.CLIENT_SECRET,
                      algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        return jwt.decode(token, settings.CLIENT_SECRET,
                          algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def verify_token_and_permissions(
    token: str,
    required_roles: Optional[List[str]] = None,
    required_permissions: Optional[List[str]] = None
) -> Optional[dict]:
    """Verify token and check if user has required roles and permissions"""
    try:
        payload = jwt.decode(token, settings.CLIENT_SECRET,
                             algorithms=[settings.ALGORITHM])

        if required_roles and not set(payload.get("roles", [])).intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User doesn't have the required roles"
            )

        if required_permissions and not set(payload.get("permissions", [])).intersection(required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User doesn't have the required permissions"
            )

        return payload
    except JWTError:
        return None
