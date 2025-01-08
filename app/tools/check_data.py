from app.core.database import async_session
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from typing import Dict, Any

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)


async def get_table_count() -> Dict[str, int]:
    """Get row count from all tables"""
    tables = [
        'unit',
        'user',
        'role',
        'privilege',
        'session',
        'user_role',
        'role_privilege',
    ]

    counts = {}
    async with async_session() as db:
        for table in tables:
            try:
                query = text(f"SELECT COUNT(*) FROM {table}")
                result = await db.execute(query)
                count = result.scalar()
                counts[table] = count
            except Exception as e:
                print(f"Error counting {table}: {str(e)}")
                counts[table] = -1

    return counts


async def get_table_data(table_name: str) -> list[Dict[str, Any]]:
    """Get all rows from a table"""
    async with async_session() as db:
        try:
            query = text(f"SELECT * FROM {table_name}")
            result = await db.execute(query)
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"Error getting data from {table_name}: {str(e)}")
            return []


async def main():
    print("\nChecking database data...")
    print("=" * 50)

    # Get row counts
    counts = await get_table_count()
    print("\nTable Row Counts:")
    print("-" * 30)
    for table, count in counts.items():
        print(f"{table:<20} {count} rows")

    # Get detailed data for important tables
    important_tables = ['unit', 'user', 'role', 'privilege']

    for table in important_tables:
        print(f"\n{table.upper()} Table Data:")
        print("-" * 30)
        rows = await get_table_data(table)
        for row in rows:
            print(row)

    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
