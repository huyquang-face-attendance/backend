from app.services.area import (
    get_area_by_id,
    get_areas,
    create_area,
    update_area,
    delete_area,
    get_area_by_name,
)

from app.services.camera import (
    get_camera_by_id,
    get_cameras,
    create_camera,
    update_camera,
    delete_camera,
    get_cameras_by_area_id,
    get_cameras_by_server_id,
    get_cameras_with_functions
)

from app.services.department import (
    get_department_by_id,
    get_departments,
    create_department,
    update_department,
    delete_department
)

from app.services.person import (
    get_person_by_id,
    get_persons,
    create_person,
    update_person,
    delete_person,
    get_person_by_code
)

from app.services.person_event import (
    get_person_event_by_id,
    get_person_events,
    create_person_event,
    delete_person_event,
    get_latest_person_event
)

from app.services.person_type import (
    get_person_type_by_id,
    get_person_types,
    create_person_type,
    update_person_type,
    delete_person_type,
)

from app.services.server import (
    get_server_by_id,
    get_servers,
    create_server,
    update_server,
    delete_server,
    get_server_by_name,
    get_servers_with_cameras
)

from app.services.function import (
    get_function_by_id,
    get_functions,
    create_function,
    update_function,
    delete_function,
    get_function_by_name,
    get_functions_with_cameras,
    get_functions_by_camera_id
)

from app.services.auth import (
    authenticate_user,
)

from app.services.role import (
    get_role_by_id,
    get_roles,
    create_role,
    update_role,
    delete_role,
    get_role_by_name,
    get_roles_with_privileges
)

from app.services.privilege import (
    get_privilege_by_id,
    get_privileges,
    create_privilege,
    update_privilege,
    delete_privilege,
    get_privilege_by_name
)

from app.services.session import (
    get_session_by_id,
    get_sessions,
    create_session,
    delete_session,
    get_active_sessions_by_user_id
)

from app.services.user import (
    get_user_by_id,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_username,
    get_users_with_roles
)

from app.services.unit import (
    get_unit_by_id,
    get_units,
    create_unit,
    update_unit,
    delete_unit,
    get_unit_by_code
)

from app.services.ai import detect_face

__all__ = [
    # ... existing exports ...
    'detect_face',
]
