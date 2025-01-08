from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    user,
    role,
    unit,
    privilege,
    area,
    camera,
    department,
    person,
    person_event,
    person_type,
)

api_router = APIRouter()

# Authentication and User Management
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(role.router, prefix="/roles", tags=["Roles"])
api_router.include_router(unit.router, prefix="/units", tags=["Units"])
api_router.include_router(
    privilege.router, prefix="/privileges", tags=["Privileges"])

# Location Management
api_router.include_router(area.router, prefix="/areas", tags=["Areas"])
api_router.include_router(
    department.router, prefix="/departments", tags=["Departments"])

# Device Management
api_router.include_router(camera.router, prefix="/cameras", tags=["Cameras"])


# Person Management
api_router.include_router(person.router, prefix="/persons", tags=["Persons"])
api_router.include_router(
    person_type.router, prefix="/person-types", tags=["Person Types"])
api_router.include_router(
    person_event.router, prefix="/person-events", tags=["Person Events"])
