from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.services.user import get_user_by_username
from app.services.session import create_session
from app.schemas import SessionCreate
from app.schemas.auth import (
    TokenResponse,
    TokenData,
)
from app.core.security import verify_password
from app.models import User

settings = get_settings()


async def authenticate_user(db: AsyncSession, user_name: str, password: str):
    user = await get_user_by_username(db, user_name)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_name or password"
        )

    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_name or password"
        )

    return user


async def create_token_response(db: AsyncSession, user: User, client_id: str) -> TokenResponse:
    access_token_expires = settings.datetime_now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = settings.datetime_now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    token_data = TokenData(
        sub=str(user.id),
        username=user.username,
        client_id=client_id
    )

    access_token = create_access_token(data=token_data.model_dump())
    refresh_token = create_refresh_token(
        data={"sub": token_data.sub, "client_id": client_id}
    )
    session_data = SessionCreate(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=access_token_expires,
        refresh_expires_at=refresh_token_expires
    )
    await create_session(db, session_data)
    return TokenResponse(
        accessToken=access_token,
        accessTokenExpires=access_token_expires,
        refreshToken=refresh_token,
        refreshTokenExpires=refresh_token_expires,
        fullName=user.full_name,
        userName=user.username,
        unitId=user.unit_id,
        userId=user.id
    )
