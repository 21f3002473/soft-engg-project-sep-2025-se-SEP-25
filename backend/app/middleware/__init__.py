from enum import Enum
from typing import List

from app.database import User
from fastapi import Depends, HTTPException, status


class Role(str, Enum):
    """User roles in the system"""

    ROOT = "root"
    HUMAN_RESOURCE = "hr"
    PRODUCT_MANAGER = "pm"
    EMPLOYEE = "employee"


ROLE_HIERARCHY = {
    Role.ROOT: [Role.ROOT, Role.HUMAN_RESOURCE, Role.PRODUCT_MANAGER, Role.EMPLOYEE],
    Role.HUMAN_RESOURCE: [Role.HUMAN_RESOURCE, Role.EMPLOYEE],
    Role.PRODUCT_MANAGER: [Role.PRODUCT_MANAGER, Role.EMPLOYEE],
    Role.EMPLOYEE: [Role.EMPLOYEE],
}


def check_role_access(user_role: str, allowed_roles: List[Role]) -> bool:
    """Check if user's role is in the allowed roles (considering hierarchy)"""
    try:
        role = Role(user_role)
        user_allowed_roles = ROLE_HIERARCHY.get(role, [])
        return any(allowed_role in user_allowed_roles for allowed_role in allowed_roles)
    except ValueError:
        return False


class RoleChecker:
    """
    Dependency class to check if user has required roles.
    Includes authentication via get_current_active_user.

    Usage in routes:
    def get(self, current_user: User = Depends(require_pm())):
    """

    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(lambda: None)) -> User:
        
        from app.controllers import get_current_active_user

        
        if current_user is None:
            
            pass

        if not check_role_access(current_user.role, self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}. Your role: {current_user.role}",
            )
        return current_user


def require_root():
    """Require ROOT role (superuser only)"""
    from app.controllers import get_current_active_user

    def check_root(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_role_access(current_user.role, [Role.ROOT]):
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
        if not check_role_access(current_user.role, [Role.ROOT, Role.HUMAN_RESOURCE]):
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
        if not check_role_access(current_user.role, [Role.ROOT, Role.PRODUCT_MANAGER]):
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
            [Role.ROOT, Role.HUMAN_RESOURCE, Role.PRODUCT_MANAGER, Role.EMPLOYEE],
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
            current_user.role, [Role.ROOT, Role.HUMAN_RESOURCE, Role.PRODUCT_MANAGER]
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
