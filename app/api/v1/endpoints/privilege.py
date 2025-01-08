from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_permissions
from app.services import privilege as privilege_service
from app.schemas.privilege import (
    Privilege, PrivilegeCreate, PrivilegeUpdate
)

router = APIRouter()


@router.get("", response_model=List[Privilege])
async def list_privileges(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewPrivilege"]))
):
    return await privilege_service.get_privileges(db, skip=skip, limit=limit)


@router.post("", response_model=Privilege)
async def create_privilege(
    privilege_data: PrivilegeCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManagePrivilege"]))
):
    return await privilege_service.create_privilege(db, privilege_data)


@router.get("/{privilege_id}", response_model=Privilege)
async def get_privilege(
    privilege_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewPrivilege"]))
):
    privilege = await privilege_service.get_privilege_by_id(db, privilege_id)
    if not privilege:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privilege not found"
        )
    return privilege


@router.put("/{privilege_id}", response_model=Privilege)
async def update_privilege(
    privilege_id: str,
    privilege_data: PrivilegeUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManagePrivilege"]))
):
    privilege = await privilege_service.update_privilege(
        db, privilege_id, privilege_data)
    if not privilege:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privilege not found"
        )
    return privilege


@router.delete("/{privilege_id}")
async def delete_privilege(
    privilege_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManagePrivilege"]))
):
    if not await privilege_service.delete_privilege(db, privilege_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privilege not found"
        )
    return {"message": "Privilege successfully deleted"}
