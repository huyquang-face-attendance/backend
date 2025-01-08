"""create_rbac_tables

Revision ID: 01_create_rbac_tables
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01_create_rbac_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create person_type table
    op.create_table(
        'person_type',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create server table
    op.create_table(
        'server',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create function table
    op.create_table(
        'function',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create role_privilege table
    op.create_table(
        'role_privilege',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('privilege_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('role_id', 'privilege_id')
    )

    # Create user_role table
    op.create_table(
        'user_role',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create camera_function table
    op.create_table(
        'camera_function',
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('function_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('camera_id', 'function_id')
    )

    # Create role table
    op.create_table(
        'role',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create privilege table
    op.create_table(
        'privilege',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('method_route', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create session table
    op.create_table(
        'session',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('unit_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create unit table
    op.create_table(
        'unit',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create area table
    op.create_table(
        'area',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create camera table
    op.create_table(
        'camera',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('area_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('link', sa.String(100)),
        sa.Column('server_id', sa.Integer()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create department table
    op.create_table(
        'department',
        sa.Column('id', sa.Integer(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create person table
    op.create_table(
        'person',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.Integer()),
        sa.Column('gender', sa.Boolean()),
        sa.Column('birthday', sa.DateTime()),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('image', sa.String(100)),
        sa.Column('identity_card', sa.String(20)),
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(50)),
        sa.Column('feature', sa.ARRAY(
            sa.Float(), dimensions=1)),  # vector(512)
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create person_event table
    op.create_table(
        'person_event',
        sa.Column('event_id', sa.String(36), nullable=False),
        sa.Column('person_id', sa.String(36), nullable=True),
        sa.Column('access_time', sa.DateTime(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('image', sa.Text(), nullable=False),
        sa.Column('video', sa.Text()),
        sa.Column('feature', sa.ARRAY(
            sa.Float(), dimensions=1)),  # vector(512)
        sa.Column('age', sa.Integer()),
        sa.Column('gender', sa.Boolean()),
        sa.Column('score', sa.Float()),
        sa.Column('quality', sa.Float()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('status', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('event_id'),
        sa.UniqueConstraint('event_id', name='uq_person_event_event_id'),
        # Add indexes
        sa.Index('ix_person_event_person_id', 'person_id'),
        sa.Index('ix_person_event_device_id', 'device_id'),
        sa.Index('ix_person_event_access_time', 'access_time'),
        sa.Index('ix_person_event_deleted_at', 'deleted_at'),
        sa.Index('ix_person_event_person_time', 'person_id', 'access_time'),
        sa.Index('ix_person_event_device_time', 'device_id', 'access_time')
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_role', 'role_privilege', 'role',
                          ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_privilege', 'role_privilege', 'privilege',
                          ['privilege_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_user', 'user_role', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_role_user', 'user_role', 'role',
                          ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_camera', 'camera_function', 'camera',
                          ['camera_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_function', 'camera_function', 'function',
                          ['function_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_session_user', 'session', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_user_unit', 'user', 'unit',
                          ['unit_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_unit_parent', 'unit', 'unit',
                          ['parent_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_area_unit', 'area', 'unit',
                          ['unit_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_camera_area', 'camera', 'area',
                          ['area_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_camera_server', 'camera', 'server',
                          ['server_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_department_unit', 'department', 'unit',
                          ['unit_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_department_parent', 'department', 'department',
                          ['parent_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_person_department', 'person', 'department',
                          ['department_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_person_event_person', 'person_event', 'person',
                          ['person_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_person_event_device', 'person_event', 'camera',
                          ['device_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_person_event_device',
                       'person_event', type_='foreignkey')
    op.drop_constraint('fk_person_event_person',
                       'person_event', type_='foreignkey')
    op.drop_constraint('fk_person_department', 'person', type_='foreignkey')
    op.drop_constraint('fk_department_parent',
                       'department', type_='foreignkey')
    op.drop_constraint('fk_department_unit', 'department', type_='foreignkey')
    op.drop_constraint('fk_camera_server', 'camera', type_='foreignkey')
    op.drop_constraint('fk_camera_area', 'camera', type_='foreignkey')
    op.drop_constraint('fk_area_unit', 'area', type_='foreignkey')
    op.drop_constraint('fk_unit_parent', 'unit', type_='foreignkey')
    op.drop_constraint('fk_user_unit', 'user', type_='foreignkey')
    op.drop_constraint('fk_session_user', 'session', type_='foreignkey')
    op.drop_constraint('fk_function', 'camera_function', type_='foreignkey')
    op.drop_constraint('fk_camera', 'camera_function', type_='foreignkey')
    op.drop_constraint('fk_role_user', 'user_role', type_='foreignkey')
    op.drop_constraint('fk_user', 'user_role', type_='foreignkey')
    op.drop_constraint('fk_privilege', 'role_privilege', type_='foreignkey')
    op.drop_constraint('fk_role', 'role_privilege', type_='foreignkey')

    # Drop tables in reverse order
    op.drop_table('person_event')
    op.drop_table('person')
    op.drop_table('department')
    op.drop_table('camera')
    op.drop_table('area')
    op.drop_table('unit')
    op.drop_table('user')
    op.drop_table('session')
    op.drop_table('privilege')
    op.drop_table('role')
    op.drop_table('camera_function')
    op.drop_table('user_role')
    op.drop_table('role_privilege')
    op.drop_table('function')
    op.drop_table('server')
    op.drop_table('person_type')
