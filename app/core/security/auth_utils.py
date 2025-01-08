from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user import get_user_by_id
from .token_utils import verify_token
from app.models.user import User
from app.core.config import get_settings
from app.services import session as session_service

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    session = await session_service.get_session_by_access_token(db, token)
    if not session:
        raise credentials_exception

    user = await get_user_by_id(db, session.user_id)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated user and verify they are active"""
    if not current_user.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def has_role(payload: dict, role: str) -> bool:
    """Check if user has a specific role"""
    return role in set(payload.get("roles", []))


def has_permission(payload: dict, permission: str) -> bool:
    """Check if user has a specific permission"""
    return permission in set(payload.get("permissions", []))


def has_any_role(payload: dict, roles: List[str]) -> bool:
    """Check if user has any of the specified roles"""
    user_roles = set(payload.get("roles", []))
    return bool(user_roles.intersection(roles))


def has_any_permission(payload: dict, permissions: List[str]) -> bool:
    """Check if user has any of the specified permissions"""
    user_permissions = set(payload.get("permissions", []))
    return bool(user_permissions.intersection(permissions))


def require_permissions(required_permissions: List[str]):
    """Dependency for requiring specific permissions"""
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        from app.services.user import get_user_privileges

        user_permissions = await get_user_privileges(db, current_user.id)
        if not set(required_permissions).intersection(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return permission_dependency


def get_current_session_id(token: str = Depends(oauth2_scheme)) -> int:
    """Get the current session ID from the token"""
    payload = verify_token(token)
    return payload.get("session_id")
