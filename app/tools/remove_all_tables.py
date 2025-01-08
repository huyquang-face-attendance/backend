import sys
from pathlib import Path
# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

import asyncio
from sqlalchemy import inspect, text
from app.core.database import engine


async def remove_all_tables():
    """Remove all tables from the database"""
    async with engine.connect() as conn:
        def get_table_names(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()

        existing_tables = await conn.run_sync(get_table_names)

        print("\nRemoving database tables...")
        print("=" * 50)

        # Ensure any existing transaction is rolled back before starting a new one
        await conn.rollback()

        # Start a new transaction
        async with conn.begin():
            for table in existing_tables:
                try:
                    # Quote the table name to handle reserved words like "user"
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    print(f"{table:<20} ✅ Removed")
                except Exception as e:
                    print(f"{table:<20} ❌ Error: {str(e)}")
                    await conn.rollback()
                    raise

        print("=" * 50)
        print("✅ All tables have been removed!")


async def main():
    try:
        await remove_all_tables()
    except Exception as e:
        print(f"Error removing tables: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
