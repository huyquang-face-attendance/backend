from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.database import get_db
from app.services.user import get_user_by_id
from app.services.session import get_session_by_refresh_token, invalidate_session
from app.core.security import get_current_session_id
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    LogoutResponse
)
from app.services import client as client_service
from app.services.auth import authenticate_user, create_token_response

router = APIRouter()

settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Handle password-based authentication"""
    if not await client_service.verify_client(request.client_id, request.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not request.user_name or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_name and password required"
        )

    user = await authenticate_user(db, request.user_name, request.password)
    return await create_token_response(db, user, request.client_id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle refresh token authentication"""
    if not await client_service.verify_client(request.client_id, request.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token required"
        )

    session = await get_session_by_refresh_token(db, request.refresh_token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if session.refresh_expires_at < settings.datetime_now :
        await invalidate_session(db, session.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    user = await get_user_by_id(db, session.user_id)

    if not user or user.deleted_at:
        await invalidate_session(db, session.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    await invalidate_session(db, session.id)
    return await create_token_response(db, user, request.client_id)


@ router.post("/logout", response_model=LogoutResponse)
async def logout(
    db: AsyncSession = Depends(get_db),
    session_id: int = Depends(get_current_session_id)
):
    await invalidate_session(db, session_id)
    return LogoutResponse(message="Successfully logged out")
