import sys
from pathlib import Path
# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department
from app.core.config import get_settings

settings = get_settings()

async def remove_test_department(db: AsyncSession) -> bool:
    """Remove test department with specific attributes"""
    department = await db.get(Department, 1)
    if not department:
        return False
        
    if (department.name == "Atin T4" and 
        department.code == "T4" and
        department.unit_id == 1 and 
        department.parent_id == 1):
        await db.delete(department)
        await db.commit()
        return True
        
    return False
