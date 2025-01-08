from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Server
from app.schemas.server import ServerCreate, ServerUpdate, Server as ServerSchema
from app.schemas.common import PaginationResponse
from app.core.config import get_settings
from .base import BasePaginationService

settings = get_settings()

# Create server pagination service
server_pagination = BasePaginationService[Server, ServerSchema](
    model=Server,
    schema=ServerSchema
)


async def get_server_by_id(db: AsyncSession, server_id: int) -> Optional[Server]:
    query = select(Server).where(
        Server.id == server_id,
        Server.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_servers(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10
) -> PaginationResponse[ServerSchema]:
    """Get paginated list of servers"""
    return await server_pagination.get_paginated(
        db,
        page=page,
        size=size
    )


async def create_server(db: AsyncSession, server_data: ServerCreate) -> Server:
    db_server = Server(**server_data.model_dump())
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server


async def update_server(
    db: AsyncSession,
    server_id: int,
    server_data: ServerUpdate
) -> Optional[Server]:
    server = await get_server_by_id(db, server_id)
    if not server:
        return None

    update_data = server_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(server, field, value)

    await db.commit()
    await db.refresh(server)
    return server


async def delete_server(db: AsyncSession, server_id: int) -> bool:
    server = await get_server_by_id(db, server_id)
    if not server:
        return False

    server.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_server_by_name(db: AsyncSession, name: str) -> Optional[Server]:
    query = select(Server).where(
        Server.name == name,
        Server.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_servers_with_cameras(db: AsyncSession) -> List[Server]:
    query = select(Server).where(
        Server.deleted_at.is_(None)
    ).options(
        selectinload(Server.cameras)
    )
    result = await db.execute(query)
    return result.scalars().all()
