from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_permissions
from app.services import user as user_service
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.common import PaginationResponse
from app.core.config import get_settings

settings = get_settings()

router = APIRouter()


@router.get("", response_model=PaginationResponse[User])
async def get_users(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(
        [settings.get_privilege("user.view")]))
):
    users = await user_service.get_users(db, page=page, size=page_size)
    return users


@router.post("", response_model=User)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(
        [settings.get_privilege("user.manage")]))
):
    user = await user_service.create_user(db, user_data)
    return user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(
        [settings.get_privilege("user.view")]))
):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(
        [settings.get_privilege("user.manage")]))
):
    user = await user_service.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}")
async def delete_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(
        [settings.get_privilege("user.manage")]))
):
    result = await user_service.delete_user(db, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User successfully deleted"}
