import sys
from pathlib import Path
import yaml

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)


from app.core.database import async_session, engine
from sqlalchemy import inspect, text
import asyncio


# Load default data from YAML
default_data_file = Path(project_root) / "resources" / \
    "configs" / "default_data.yaml"
with open(default_data_file, 'r') as f:
    DEFAULT_DATA = yaml.safe_load(f)


async def check_tables():
    required_tables = [
        'person_type', 'server', 'function', 'role_privilege', 'user_role',
        'camera_function', 'role', 'user', 'unit', 'area', 'camera',
        'department', 'person', 'person_event', 'privilege', 'session'
    ]

    async with engine.connect() as conn:
        def get_table_names(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()

        existing_tables = await conn.run_sync(get_table_names)

        print("\nChecking database tables...")
        print("=" * 50)

        all_tables_exist = True
        for table in required_tables:
            exists = table in existing_tables
            status = "✅ Found" if exists else "❌ Missing"
            print(f"{table:<20} {status}")

            if not exists:
                all_tables_exist = False

        print("=" * 50)
        if all_tables_exist:
            print("✅ All required tables exist!")
        else:
            print("❌ Some tables are missing. Please run migrations first.")

        return all_tables_exist


async def check_default_data():
    """Check if default data exists in tables"""
    async with async_session() as db:
        print("\nChecking default data...")
        print("=" * 50)

        # Check person_type
        query = text(
            "SELECT COUNT(*) FROM person_type WHERE id = 1 AND name = 'Staff'")
        result = await db.execute(query)
        count = result.scalar()
        print(
            f"person_type {'✅ Found' if count > 0 else '❌ Missing'} default Staff type")

        # Check server
        query = text(
            "SELECT COUNT(*) FROM server WHERE id = 1 AND name = 'Server 1'")
        result = await db.execute(query)
        count = result.scalar()
        print(
            f"server {'✅ Found' if count > 0 else '❌ Missing'} default Server")

        # Check function
        query = text(
            "SELECT COUNT(*) FROM function WHERE id = 1 AND name = 'Face Recognition'")
        result = await db.execute(query)
        count = result.scalar()
        print(
            f"function {'✅ Found' if count > 0 else '❌ Missing'} default Function")

        # Check unit
        query = text(
            "SELECT COUNT(*) FROM unit WHERE id = 1 AND name = 'Công ty phần mềm ATIN'")
        result = await db.execute(query)
        count = result.scalar()
        print(f"unit {'✅ Found' if count > 0 else '❌ Missing'} default Unit")

        # Check role
        query = text(
            "SELECT COUNT(*) FROM role WHERE id = 1 AND name = 'Admin'")
        result = await db.execute(query)
        count = result.scalar()
        print(
            f"role {'✅ Found' if count > 0 else '❌ Missing'} default Admin role")

        # Check privileges
        query = text("SELECT COUNT(*) FROM privilege")
        result = await db.execute(query)
        count = result.scalar()
        expected_privileges = len(DEFAULT_DATA['privilege'])
        print(
            f"privilege {'✅ Found' if count >= expected_privileges else '❌ Missing'} default privileges ({count}/{expected_privileges})")

        print("=" * 50)


async def main():
    try:
        tables_exist = await check_tables()
        if tables_exist:
            await check_default_data()
    except Exception as e:
        print(f"Error checking tables: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
