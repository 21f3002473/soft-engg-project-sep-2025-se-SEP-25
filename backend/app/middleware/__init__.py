from enum import Enum
from typing import List

from app.database import RoleEnum, User
from fastapi import Depends, HTTPException, status


ROLE_HIERARCHY = {
    RoleEnum.ROOT: [
        RoleEnum.ROOT,
        RoleEnum.HUMAN_RESOURCE,
        RoleEnum.PRODUCT_MANAGER,
        RoleEnum.EMPLOYEE,
    ],
    RoleEnum.HUMAN_RESOURCE: [RoleEnum.HUMAN_RESOURCE, RoleEnum.EMPLOYEE],
    RoleEnum.PRODUCT_MANAGER: [RoleEnum.PRODUCT_MANAGER, RoleEnum.EMPLOYEE],
    RoleEnum.EMPLOYEE: [RoleEnum.EMPLOYEE],
}


class Permission(str, Enum):
    """System permissions mapped to roles"""

    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    UPDATE_USER_ROLE = "update_user_role"
    VIEW_ALL_USERS = "view_all_users"

    MANAGE_EMPLOYEES = "manage_employees"
    VIEW_EMPLOYEE_RECORDS = "view_employee_records"
    MANAGE_PAYROLL = "manage_payroll"
    MANAGE_RECRUITMENT = "manage_recruitment"

    MANAGE_PRODUCTS = "manage_products"
    VIEW_PRODUCTS = "view_products"
    MANAGE_PROJECTS = "manage_projects"
    VIEW_ANALYTICS = "view_analytics"

    VIEW_OWN_PROFILE = "view_own_profile"
    UPDATE_OWN_PROFILE = "update_own_profile"

    VIEW_SYSTEM_LOGS = "view_system_logs"
    GENERATE_REPORTS = "generate_reports"
    SYSTEM_CONFIG = "system_config"


ROLE_PERMISSIONS = {
    RoleEnum.ROOT: [perm for perm in Permission],
    RoleEnum.HUMAN_RESOURCE: [
        Permission.VIEW_ALL_USERS,
        Permission.MANAGE_EMPLOYEES,
        Permission.VIEW_EMPLOYEE_RECORDS,
        Permission.MANAGE_PAYROLL,
        Permission.MANAGE_RECRUITMENT,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
    ],
    RoleEnum.PRODUCT_MANAGER: [
        Permission.MANAGE_PRODUCTS,
        Permission.VIEW_PRODUCTS,
        Permission.MANAGE_PROJECTS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_EMPLOYEE_RECORDS,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
    ],
    RoleEnum.EMPLOYEE: [
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
    ],
}


def check_role_access(user_role: str, allowed_roles: List[RoleEnum]) -> bool:
    """Check if user's role is in the allowed roles (considering hierarchy)"""
    try:
        role = RoleEnum(user_role)
        user_allowed_roles = ROLE_HIERARCHY.get(role, [])
        return any(allowed_role in user_allowed_roles for allowed_role in allowed_roles)
    except ValueError:
        return False


def require_root():
    """Require ROOT role (superuser only)"""
    from app.controllers import get_current_active_user

    def check_root(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(current_user.role, [RoleEnum.ROOT]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: ROOT. Your role: {current_user.role}",
            )
        return current_user

    return check_root


def require_hr():
    """Require Human Resource role or higher"""
    from app.controllers import get_current_active_user

    def check_hr(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(
            current_user.role, [RoleEnum.ROOT, RoleEnum.HUMAN_RESOURCE]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: ROOT or HR. Your role: {current_user.role}",
            )
        return current_user

    return check_hr


def require_pm():
    """Require Product Manager role or higher"""
    from app.controllers import get_current_active_user

    def check_pm(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(
            current_user.role, [RoleEnum.ROOT, RoleEnum.PRODUCT_MANAGER]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: ROOT or PM. Your role: {current_user.role}",
            )
        return current_user

    return check_pm


def require_employee():
    """Require any authenticated user (employee or higher)"""
    from app.controllers import get_current_active_user

    def check_employee(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(
            current_user.role,
            [
                RoleEnum.ROOT,
                RoleEnum.HUMAN_RESOURCE,
                RoleEnum.PRODUCT_MANAGER,
                RoleEnum.EMPLOYEE,
            ],
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Your role: {current_user.role}",
            )
        return current_user

    return check_employee


def require_hr_or_pm():
    """Require either HR or PM role"""
    from app.controllers import get_current_active_user

    def check_hr_or_pm(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(
            current_user.role,
            [RoleEnum.ROOT, RoleEnum.HUMAN_RESOURCE, RoleEnum.PRODUCT_MANAGER],
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: ROOT, HR or PM. Your role: {current_user.role}",
            )
        return current_user

    return check_hr_or_pm


def can_manage_employees():
    """Check if user can manage employees (HR or ROOT)"""
    return require_hr()


def can_manage_products():
    """Check if user can manage products (PM or ROOT)"""
    return require_pm()


def can_view_system_logs():
    """Check if user can view system logs (ROOT only)"""
    return require_root()
