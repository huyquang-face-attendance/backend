from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_permissions
from app.services import role as role_service
from app.schemas.role import Role, RoleCreate, RoleUpdate

router = APIRouter()


@router.get("", response_model=List[Role])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewRole"]))
):
    return await role_service.get_roles(db, skip=skip, limit=limit)


@router.post("", response_model=Role)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageRole"]))
):
    return await role_service.create_role(db, role_data)


@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewRole"]))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageRole"]))
):
    role = await role_service.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageRole"]))
):
    if not await role_service.delete_role(db, role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return {"message": "Role successfully deleted"}


@router.post("/{role_id}/privileges/{privilege_id}")
async def add_privilege_to_role(
    role_id: int,
    privilege_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageRole"]))
):
    if not await role_service.add_privilege_to_role(db, role_id, privilege_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or privilege not found"
        )
    return {"message": "Privilege added to role successfully"}


@router.delete("/{role_id}/privileges/{privilege_id}")
async def remove_privilege_from_role(
    role_id: int,
    privilege_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageRole"]))
):
    if not await role_service.remove_privilege_from_role(db, role_id, privilege_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or privilege not found"
        )
    return {"message": "Privilege removed from role successfully"}
