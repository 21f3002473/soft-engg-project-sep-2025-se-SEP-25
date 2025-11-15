from enum import Enum
from functools import wraps
from typing import Callable, List

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


##########################################################
#  this dummy data access and we dont need it for now
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


# this dummy data access and we dont need it for now
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
###############################################################


def check_permission(user_role: str, required_permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    try:
        role = RoleEnum(user_role)
        return required_permission in ROLE_PERMISSIONS.get(role, [])
    except ValueError:
        return False


def check_role_access(user_role: str, allowed_roles: List[RoleEnum]) -> bool:
    """Check if user's role is in the allowed roles (considering hierarchy)"""
    try:
        role = RoleEnum(user_role)
        user_allowed_roles = ROLE_HIERARCHY.get(role, [])
        return any(allowed_role in user_allowed_roles for allowed_role in allowed_roles)
    except ValueError:
        return False


class RoleChecker:
    """
    Dependency class to check if user has required roles.

    Usage in routes:
    @app.get("/admin", dependencies=[Depends(RoleChecker([RoleEnum.ROOT]))])
    """

    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not check_role_access(current_user.role, self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}. Your role: {current_user.role}",
            )
        return current_user


class PermissionChecker:
    """
    Dependency class to check if user has required permissions.

    Usage in routes:
    @app.get("/users", dependencies=[Depends(PermissionChecker([Permission.VIEW_ALL_USERS]))])
    """

    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        for permission in self.required_permissions:
            if not check_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission.value}. Your role: {current_user.role}",
                )
        return current_user


def require_root() -> RoleChecker:
    """Require ROOT role (superuser only)"""
    return RoleChecker([RoleEnum.ROOT])


def require_hr() -> RoleChecker:
    """Require Human Resource role or higher"""
    return RoleChecker([RoleEnum.ROOT, RoleEnum.HUMAN_RESOURCE])


def require_pm() -> RoleChecker:
    """Require Product Manager role or higher"""
    return RoleChecker([RoleEnum.ROOT, RoleEnum.PRODUCT_MANAGER])


def require_employee() -> RoleChecker:
    """Require any authenticated user (employee or higher)"""
    return RoleChecker(
        [
            RoleEnum.ROOT,
            RoleEnum.HUMAN_RESOURCE,
            RoleEnum.PRODUCT_MANAGER,
            RoleEnum.EMPLOYEE,
        ]
    )


def require_hr_or_pm() -> RoleChecker:
    """Require either HR or PM role"""
    return RoleChecker(
        [RoleEnum.ROOT, RoleEnum.HUMAN_RESOURCE, RoleEnum.PRODUCT_MANAGER]
    )


def can_manage_employees() -> PermissionChecker:
    """Check if user can manage employees"""
    return PermissionChecker([Permission.MANAGE_EMPLOYEES])


def can_manage_products() -> PermissionChecker:
    """Check if user can manage products"""
    return PermissionChecker([Permission.MANAGE_PRODUCTS])


def can_view_system_logs() -> PermissionChecker:
    """Check if user can view system logs"""
    return PermissionChecker([Permission.VIEW_SYSTEM_LOGS])
