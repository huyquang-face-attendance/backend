import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.core.config import get_settings
from sqlalchemy import table, column, select, insert
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio


settings = get_settings()


async def create_demo_user():
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
                     column('password_hash', sa.Text),
                     column('full_name', sa.String),
                     column('unit_id', sa.Integer),
                     column('created_at', sa.DateTime),
                     column('updated_at', sa.DateTime),
                     column('deleted_at', sa.DateTime),
                     column('status', sa.Boolean))

        user_role = table('user_role',
                          column('user_id', sa.Integer),
                          column('role_id', sa.Integer),
                          column('created_at', sa.DateTime))

        # Check if demo user exists
        result = await session.execute(
            select(user).where(user.c.username == "demo")
        )
        if result.first():
            print("Demo user already exists")
            return

        # Create demo user
        user_data = {
            'username': 'demo',
            'password_hash': get_password_hash('Demo@123456'),
            'full_name': 'Demo User',
            'status': True,
            'created_at': settings.datetime_now
        }
        result = await session.execute(insert(user).values(user_data))
        user_id = result.inserted_primary_key[0]

        # Associate with admin role (assuming role_id 1 is admin from default_data)
        user_role_data = {
            'user_id': user_id,
            'role_id': 1,
            'created_at': settings.datetime_now
        }
        await session.execute(insert(user_role).values(user_role_data))
        await session.commit()

        print("Demo user created successfully with admin privileges")

if __name__ == "__main__":
    asyncio.run(create_demo_user())
