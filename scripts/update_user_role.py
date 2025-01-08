import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import sqlalchemy as sa
from sqlalchemy import table, column, select, insert, delete
from app.core.config import get_settings



settings = get_settings()


async def update_user_role():
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Define tables using SQLAlchemy core
        user = table('user',
                     column('id', sa.Integer),
                     column('username', sa.String),
                     column('status', sa.Boolean),
                     column('deleted_at', sa.DateTime))

        user_role = table('user_role',
                          column('user_id', sa.Integer),
                          column('role_id', sa.Integer),
                          column('created_at', sa.DateTime))

        # Check if user exists and is active
        result = await session.execute(
            select(user).where(
                user.c.id == 2,
                user.c.deleted_at.is_(None),
                user.c.status == True
            )
        )
        if not result.first():
            print("User ID 2 not found or is inactive")
            return

        # Delete existing user roles
        await session.execute(
            delete(user_role).where(user_role.c.user_id == 2)
        )

        # Add admin role
        user_role_data = {
            'user_id': 2,
            'role_id': 1,  # Admin role
            'created_at': settings.datetime_now
        }
        await session.execute(insert(user_role).values(user_role_data))
        await session.commit()

        print("User role updated successfully - User ID 2 now has admin privileges")


if __name__ == "__main__":
    asyncio.run(update_user_role())
