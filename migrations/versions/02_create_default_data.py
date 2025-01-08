"""create_default_data

Revision ID: 02_create_default_data
Revises: 01_create_rbac_tables
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from app.core.security import get_password_hash
from app.core.config import get_settings
from datetime import datetime, timedelta
import yaml
from pathlib import Path

settings = get_settings()

# revision identifiers, used by Alembic.
revision = '02_create_default_data'
down_revision = '01_create_rbac_tables'
branch_labels = None
depends_on = None

# Load default data from YAML
ROOT_DIR = Path(__file__).parent.parent.parent
default_data_file = ROOT_DIR / "resources" / "configs" / "default_data.yaml"
with open(default_data_file, 'r') as f:
    DEFAULT_DATA = yaml.safe_load(f)


def upgrade() -> None:
    # Create default person type
    person_type = table('person_type',
                        column('id', sa.Integer),
                        column('name', sa.String),
                        column('status', sa.Boolean),
                        column('created_at', sa.DateTime),
                        column('updated_at', sa.DateTime),
                        column('deleted_at', sa.DateTime))
    person_type_data = [{**item, 'created_at': settings.datetime_now}
                        for item in DEFAULT_DATA['person_type']]
    op.bulk_insert(person_type, person_type_data)

    # Create default server
    server = table('server',
                   column('id', sa.Integer),
                   column('name', sa.String),
                   column('status', sa.Boolean),
                   column('created_at', sa.DateTime),
                   column('updated_at', sa.DateTime),
                   column('deleted_at', sa.DateTime))
    server_data = [{**item, 'created_at': settings.datetime_now}
                   for item in DEFAULT_DATA['server']]
    op.bulk_insert(server, server_data)

    # Create default function
    function = table('function',
                     column('id', sa.Integer),
                     column('name', sa.String),
                     column('status', sa.Boolean),
                     column('created_at', sa.DateTime),
                     column('updated_at', sa.DateTime),
                     column('deleted_at', sa.DateTime))
    function_data = [{**item, 'created_at': settings.datetime_now}
                     for item in DEFAULT_DATA['function']]
    op.bulk_insert(function, function_data)

    # Create default unit
    unit = table('unit',
                 column('id', sa.Integer),
                 column('name', sa.String),
                 column('code', sa.String),
                 column('parent_id', sa.Integer),
                 column('created_at', sa.DateTime),
                 column('updated_at', sa.DateTime),
                 column('deleted_at', sa.DateTime),
                 column('status', sa.Boolean))
    unit_data = [{**item, 'created_at': settings.datetime_now}
                 for item in DEFAULT_DATA['unit']]
    op.bulk_insert(unit, unit_data)

    # Create default role
    role = table('role',
                 column('id', sa.Integer),
                 column('name', sa.String),
                 column('description', sa.Text),
                 column('created_at', sa.DateTime),
                 column('updated_at', sa.DateTime),
                 column('deleted_at', sa.DateTime),
                 column('status', sa.Boolean))
    role_data = [{**item, 'created_at': settings.datetime_now}
                 for item in DEFAULT_DATA['role']]
    op.bulk_insert(role, role_data)

    # Create default privileges
    privilege = table('privilege',
                      column('id', sa.Integer),
                      column('name', sa.String),
                      column('description', sa.Text),
                      column('method_route', sa.String),
                      column('created_at', sa.DateTime),
                      column('updated_at', sa.DateTime),
                      column('deleted_at', sa.DateTime),
                      column('status', sa.Boolean))
    privilege_data = [{**item, 'created_at': settings.datetime_now}
                      for item in DEFAULT_DATA['privilege']]
    op.bulk_insert(privilege, privilege_data)

    # Create default admin user
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
    user_data = [{
        **item,
        'password_hash': get_password_hash(item['password']),
        'created_at': settings.datetime_now
    } for item in DEFAULT_DATA['user']]
    op.bulk_insert(user, user_data)

    # Associate admin role with privileges
    role_privilege = table('role_privilege',
                           column('role_id', sa.Integer),
                           column('privilege_id', sa.Integer),
                           column('created_at', sa.DateTime))
    role_privilege_data = [{**item, 'created_at': settings.datetime_now}
                           for item in DEFAULT_DATA['role_privilege']]
    op.bulk_insert(role_privilege, role_privilege_data)

    # Associate admin user with role
    user_role = table('user_role',
                      column('user_id', sa.Integer),
                      column('role_id', sa.Integer),
                      column('created_at', sa.DateTime))
    user_role_data = [{**item, 'created_at': settings.datetime_now}
                      for item in DEFAULT_DATA['user_role']]
    op.bulk_insert(user_role, user_role_data)


def downgrade() -> None:
    # Delete in reverse order of dependencies
    op.execute('DELETE FROM user_role')
    op.execute('DELETE FROM role_privilege')
    op.execute('DELETE FROM user')
    op.execute('DELETE FROM privilege')
    op.execute('DELETE FROM role')
    op.execute('DELETE FROM unit')
    op.execute('DELETE FROM function')
    op.execute('DELETE FROM server')
    op.execute('DELETE FROM person_type')
