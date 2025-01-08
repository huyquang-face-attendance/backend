from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from app.core.database import Base

# Association tables
role_privilege = Table(
    'role_privilege',
    Base.metadata,
    Column('role_id', Integer, ForeignKey(
        'role.id', ondelete='CASCADE'), nullable=False),
    Column('privilege_id', Integer, ForeignKey(
        'privilege.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime(timezone=False),
           server_default=func.now(), nullable=False)
)

user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False),
    Column('role_id', Integer, ForeignKey(
        'role.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime(timezone=False),
           server_default=func.now(), nullable=False)
)

camera_function = Table(
    'camera_function',
    Base.metadata,
    Column('camera_id', Integer, ForeignKey(
        'camera.id', ondelete='CASCADE'), nullable=False),
    Column('function_id', Integer, ForeignKey(
        'function.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime(timezone=False),
           server_default=func.now(), nullable=False)
)
