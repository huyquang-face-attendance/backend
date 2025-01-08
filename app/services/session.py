from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import Session
from app.schemas.session import SessionCreate
from datetime import datetime, timezone, timedelta
from app.core.config import get_settings

settings = get_settings()


async def create_session(
    db: AsyncSession,
    session_data: SessionCreate
) -> Session:
    """Create a new session"""
    db_session = Session(
        **session_data.model_dump(),
        created_at=settings.datetime_now  # Set created_at explicitly
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def get_session_by_access_token(
    db: AsyncSession,
    access_token: str
) -> Optional[Session]:
    query = (
        select(Session)
        .where(
            Session.access_token == access_token,
            Session.deleted_at.is_(None),
            Session.expires_at > settings.datetime_now
        )
        .order_by(Session.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_session_by_refresh_token(
    db: AsyncSession,
    refresh_token: str
) -> Optional[Session]:
    query = (
        select(Session)
        .where(
            Session.refresh_token == refresh_token,
            Session.deleted_at.is_(None),
            Session.refresh_expires_at > settings.datetime_now
        )
        .order_by(Session.created_at.desc())
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def invalidate_session(
    db: AsyncSession,
    session_id: int
) -> None:
    """Mark a session as deleted"""
    query = (
        select(Session)
        .where(Session.id == session_id)
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if session:
        session.deleted_at = settings.datetime_now
        await db.commit()


async def invalidate_all_user_sessions(
    db: AsyncSession,
    user_id: int
) -> None:
    """Invalidate all sessions for a user"""
    query = (
        select(Session)
        .where(
            Session.user_id == user_id,
            Session.deleted_at.is_(None)
        )
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    now = settings.datetime_now
    for session in sessions:
        session.deleted_at = now

    await db.commit()


async def get_session_by_token(
    db: AsyncSession,
    token: str
) -> Optional[Session]:
    """Get session by access token"""
    query = select(Session).where(
        Session.access_token == token,
        Session.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def cleanup_expired_refresh_tokens(db: AsyncSession) -> int:
    """Delete sessions with expired refresh tokens"""
    now = settings.datetime_now
    query = delete(Session).where(Session.refresh_expires_at < now)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount


async def get_session_by_id(db: AsyncSession, session_id: int) -> Optional[Session]:
    query = select(Session).where(
        Session.id == session_id,
        Session.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_sessions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Session]:
    query = select(Session).where(
        Session.deleted_at.is_(None)
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def delete_session(db: AsyncSession, session_id: int) -> bool:
    session = await get_session_by_id(db, session_id)
    if not session:
        return False

    session.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_active_sessions_by_user_id(
    db: AsyncSession,
    user_id: int
) -> List[Session]:
    query = select(Session).where(
        Session.user_id == user_id,
        Session.deleted_at.is_(None),
        Session.expires_at > settings.datetime_now
    ).order_by(Session.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
