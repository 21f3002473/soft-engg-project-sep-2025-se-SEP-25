from datetime import datetime
from typing import List, Optional

from app.controllers import get_current_active_user
from app.database import User, get_session
from app.database.admin_models import Backup, BackupTypeEnum, Log
from app.middleware import RoleEnum, can_view_system_logs, require_root
from fastapi import Depends, HTTPException, Query, status
from fastapi_restful import Resource
from pydantic import BaseModel, EmailStr, Field
from requests import session
from sqlmodel import Session, select

# -----------------------------
# Validators / Schemas
# -----------------------------


class AdminRegistrationValidator(BaseModel):
    """
    Validator for admin registration payload.

    Story Point: SP-ADM-001

    Attributes:
        name: Admin name (non-empty string)
        email: Admin email address (must be valid EmailStr)
        password: Admin password (minimum 6 characters)
    """

    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class AdminAddEmployeeValidator(BaseModel):
    """
    Validator for adding new employee payload.

    Story Point: SP-ADM-002

    Attributes:
        name: Employee name (non-empty string)
        role: Employee role (e.g., 'HR', 'Product Manager', 'Employee')
        email: Optional employee email address
    """

    name: str = Field(min_length=1)
    role: str = Field(
        description="Role name such as 'HR', 'Product Manager', or 'Employee'"
    )
    email: Optional[EmailStr] = None


class BackupItem(BaseModel):
    """
    Validator for individual backup configuration item.

    Story Point: SP-ADM-004

    Attributes:
        day: Day of backup (e.g., 'Monday', 'Tuesday')
        type: Backup type - must be 'full', 'incremental', or 'differential'
        datetime: Date and time of backup
    """

    day: str
    type: str = Field(pattern="^(full|incremental|differential)$")
    datetime: datetime


class BackupConfigPayload(BaseModel):
    """
    Validator for backup configuration payload.

    Story Point: SP-ADM-004

    Attributes:
        backups: List of backup configuration items
    """

    backups: List[BackupItem]


class AccountUpdatePayload(BaseModel):
    """
    Validator for admin account update payload.

    Story Point: SP-ADM-006

    Attributes:
        name: Optional new admin name
        old_password: Optional old password (required when changing password)
        new_password: Optional new password to set
    """

    name: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None


# -----------------------------
# Helpers
# -----------------------------


def _normalize_role(role_in: str) -> str:
    """
    Map friendly role names to internal Role enum values.

    Converts user-friendly role names (e.g., 'HR', 'pm') to standardized
    RoleEnum values used internally by the system.

    Args:
        role_in: User input role name (case-insensitive)

    Returns:
        Standardized role enum value string

    Raises:
        HTTPException: 422 UNPROCESSABLE_ENTITY if role is unknown
            - Detail: "Unknown role '{role_in}'. Expected one of HR, Product Manager, Employee"
    """
    value = role_in.strip().lower()
    mapping = {
        "hr": RoleEnum.HUMAN_RESOURCE.value,
        "human resource": RoleEnum.HUMAN_RESOURCE.value,
        "human_resource": RoleEnum.HUMAN_RESOURCE.value,
        "product manager": RoleEnum.PRODUCT_MANAGER.value,
        "product_manager": RoleEnum.PRODUCT_MANAGER.value,
        "pm": RoleEnum.PRODUCT_MANAGER.value,
        "employee": RoleEnum.EMPLOYEE.value,
        "root": RoleEnum.ROOT.value,
        # allow passing raw values too
        RoleEnum.HUMAN_RESOURCE.value: RoleEnum.HUMAN_RESOURCE.value,
        RoleEnum.PRODUCT_MANAGER.value: RoleEnum.PRODUCT_MANAGER.value,
        RoleEnum.EMPLOYEE.value: RoleEnum.EMPLOYEE.value,
        RoleEnum.ROOT.value: RoleEnum.ROOT.value,
    }
    if value not in mapping:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown role '{role_in}'. Expected one of HR, Product Manager, Employee",
        )
    return mapping[value]


def _backup_type_from_str(value: str) -> BackupTypeEnum:
    """
    Convert string to BackupTypeEnum.

    Validates and converts backup type string to corresponding enum value.

    Args:
        value: Backup type as string ('full', 'incremental', 'differential')

    Returns:
        BackupTypeEnum value

    Raises:
        HTTPException: 422 UNPROCESSABLE_ENTITY if type is invalid
            - Detail: "Backup type must be one of: full, incremental, differential"
    """
    try:
        return BackupTypeEnum(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Backup type must be one of: full, incremental, differential",
        )


# -----------------------------
# Resources
# -----------------------------


class AdminRegistrationResource(Resource):
    """
    Admin Registration Resource.

    Handles registration of new ROOT users (admin accounts).

    Story Point: SP-ADM-001

    Endpoint: POST /admin/register
    Required Role: None (public endpoint)
    """

    def post(
        self,
        payload: AdminRegistrationValidator,
        session: Session = Depends(get_session),
    ):
        """
        Register a new admin (ROOT) user.

        Creates a new admin account with the provided credentials. Validates that
        no user with the same email already exists in the system.

        Args:
            payload: AdminRegistrationValidator containing name, email, password
            session: Database session dependency

        Returns:
            dict: User summary with keys:
                - id: User ID
                - name: User name
                - email: User email
                - role: User role (ROOT)

        Raises:
            HTTPException: 409 CONFLICT if email already exists
                - Detail: "A user with this email already exists"
        """
        # Check if admin already exists with this email
        existing = session.exec(select(User).where(User.email == payload.email)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        password_hash, salt = User.hash_password(payload.password)
        user = User(
            name=payload.name.strip(),
            email=str(payload.email).lower(),
            password_hash=password_hash,
            salt=salt,
            role=RoleEnum.ROOT.value,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }


class AdminDashboardResource(Resource):
    """
    Admin Dashboard Resource.

    Provides system summary statistics for the admin dashboard including
    user count, log count, backup count, and current admin information.

    Story Point: SP-ADM-003

    Endpoint: GET /admin/summary
    Required Role: ROOT
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve dashboard summary statistics.

        Aggregates system statistics including total users, system logs, and
        backup configurations. Returns information about the current admin user.

        Args:
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            dict: Dashboard summary with keys:
                - userCount: Total number of users in system
                - logsCount: Total number of system logs
                - backupsCount: Total number of backups configured
                - currentAdmin: dict with id, name, email of logged-in admin

        Raises:
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        users_count = session.exec(select(User)).all()
        logs_count = session.exec(select(Log)).all()
        backups_count = session.exec(select(Backup)).all()
        return {
            "userCount": len(users_count),
            "logsCount": len(logs_count),
            "backupsCount": len(backups_count),
            "currentAdmin": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
            },
        }


class AdminEmployeeResource(Resource):
    """
    Admin Employee Management Resource.

    Handles listing all employees and creation of new employee accounts with
    role assignment and temporary password generation.

    Story Point: SP-ADM-002

    Endpoints:
        - GET /admin/employees
        - POST /admin/employees
    Required Role: ROOT
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve list of all employees/users.

        Returns a list of all users in the system with their basic information
        including id, name, email, and role.

        Args:
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            list: Array of user objects, each containing:
                - id: User ID
                - name: User name
                - email: User email
                - role: User role

        Raises:
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        users = session.exec(select(User)).all()
        return [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
            }
            for u in users
        ]

    def post(
        self,
        payload: AdminAddEmployeeValidator,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new employee/user account.

        Creates a new user with specified role. If email is not provided, generates
        one automatically from the name. Generates a temporary password and returns
        it (only shown once) for the user to change on first login.

        Args:
            payload: AdminAddEmployeeValidator with name, role, optional email
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            dict: Created user details with keys:
                - id: New user ID
                - name: User name
                - email: Generated or provided email
                - role: Assigned user role
                - temporary_password: One-time password for initial login

        Raises:
            HTTPException: 422 UNPROCESSABLE_ENTITY if role is invalid
                - Detail: "Unknown role '{role}'. Expected one of HR, Product Manager, Employee"
            HTTPException: 409 CONFLICT if email already exists
                - Detail: "A user with this email already exists"
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        role_value = _normalize_role(payload.role)

        email = str(payload.email).lower() if payload.email else None
        if email:
            exists = session.exec(select(User).where(User.email == email)).first()
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists",
                )
        else:
            # Derive a basic email when not provided
            base = payload.name.strip().lower().replace(" ", ".")
            email = f"{base}@example.com"
            # Avoid accidental collision
            suffix = 1
            while session.exec(select(User).where(User.email == email)).first():
                suffix += 1
                email = f"{base}{suffix}@example.com"

        # Generate a temporary password
        temp_password = f"Temp{datetime.utcnow().strftime('%y%m%d%H%M%S')}!"
        password_hash, salt = User.hash_password(temp_password)

        user = User(
            name=payload.name.strip(),
            email=email,
            password_hash=password_hash,
            salt=salt,
            role=role_value,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "temporary_password": temp_password,
        }


class AdminBackupResource(Resource):
    """
    Admin Backup Configuration Resource.

    Manages backup schedule and configuration. Allows viewing current backup
    schedules and updating the backup configuration.

    Story Point: SP-ADM-004

    Endpoints:
        - GET /admin/backup-config
        - PUT /admin/backup-config
    Required Role: ROOT
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve current backup configuration.

        Returns list of all configured backups with their schedule and type.

        Args:
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            list: Array of backup configurations, each containing:
                - day: Day of backup
                - type: Backup type (full, incremental, differential)
                - datetime: ISO format datetime of backup

        Raises:
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        items = session.exec(select(Backup)).all()
        return [
            {
                "day": b.day,
                "type": b.backup_type.value,
                "datetime": b.date_time.isoformat(),
            }
            for b in items
        ]

    def put(
        self,
        payload: BackupConfigPayload,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Update backup configuration.

        Replaces the entire backup configuration. Deletes all existing backups
        and creates new ones from the provided payload. Automatically logs each
        backup creation to the system log.

        Args:
            payload: BackupConfigPayload containing list of backup items
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            dict: Confirmation with keys:
                - message: Success message
                - count: Number of backups configured

        Raises:
            HTTPException: 422 UNPROCESSABLE_ENTITY if backup type is invalid
                - Detail: "Backup type must be one of: full, incremental, differential"
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        # Replace existing configuration
        existing = session.exec(select(Backup)).all()
        for item in existing:
            session.delete(item)
        session.commit()

        for item in payload.backups:
            backup = Backup(
                day=item.day,
                backup_type=_backup_type_from_str(item.type.lower()),
                date_time=item.datetime,
            )
            session.add(backup)
            log = Log(
                user_id=current_user.id,
                text_log=f"{backup.backup_type.value.capitalize()} backup scheduled on {backup.day}",
            )
            session.add(log)
        session.commit()

        return {
            "message": "Backup configuration updated",
            "count": len(payload.backups),
        }


class AdminLogsResource(Resource):
    """
    Admin System Logs Resource.

    Provides paginated access to system logs. Logs track all system activities
    and user actions for audit purposes.

    Story Point: SP-ADM-005

    Endpoint: GET /admin/logs
    Required Role: ROOT or higher log viewing permission
    """

    def get(
        self,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(can_view_system_logs()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve system logs with pagination.

        Returns paginated system logs ordered by most recent first. Supports
        custom limit and offset for pagination.

        Args:
            limit: Number of logs per page (1-500, default 50)
            offset: Number of logs to skip (default 0)
            current_user: Currently authenticated user dependency
            _: Log viewing permission verification dependency
            session: Database session dependency

        Returns:
            list: Array of log entries, each containing:
                - id: Log ID
                - user_id: ID of user who triggered the log
                - text: Log text description
                - time: ISO format timestamp of log entry

        Raises:
            HTTPException: 403 FORBIDDEN if user lacks log viewing permission
            HTTPException: 422 UNPROCESSABLE_ENTITY if limit or offset invalid
        """
        stmt = select(Log).order_by(Log.time.desc()).offset(offset).limit(limit)
        logs = session.exec(stmt).all()
        return [
            {
                "id": l.id,
                "user_id": l.user_id,
                "text": l.text_log,
                "time": l.time.isoformat(),
            }
            for l in logs
        ]


class AdminUpdatesResource(Resource):
    """
    Admin Software Updates Resource.

    Provides information about software version and available updates.
    Currently a placeholder for future update management functionality.

    Story Point: SP-ADM-003

    Endpoint: GET /admin/updates
    Required Role: ROOT
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
    ):
        """
        Retrieve software update status.

        Returns current software version, update availability, and last check time.
        This is currently a placeholder endpoint for future implementation.

        Args:
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency

        Returns:
            dict: Update status with keys:
                - currentVersion: Current software version
                - updateAvailable: Boolean indicating if update is available
                - lastChecked: ISO format timestamp of last update check

        Raises:
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        return {
            "currentVersion": "1.0.0",
            "updateAvailable": False,
            "lastChecked": datetime.utcnow().isoformat() + "Z",
        }


class AdminAccountResource(Resource):
    """
    Admin Account Management Resource.

    Allows admin to view and update their own account information including
    name and password changes.

    Story Point: SP-ADM-006

    Endpoints:
        - GET /admin/account
        - PUT /admin/account
    Required Role: ROOT
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
    ):
        """
        Retrieve current admin account information.

        Returns detailed information about the currently authenticated admin account.

        Args:
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency

        Returns:
            dict: Admin account details with keys:
                - id: User ID
                - name: User name
                - email: User email
                - role: User role (ROOT)

        Raises:
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        }

    def put(
        self,
        payload: AccountUpdatePayload,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        # Load the user using the same session we'll commit with
        db_user: User = session.get(User, current_user.id)
        if not db_user:
            # Defensive: should not happen because current_user was authenticated, but safe guard
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        updated = False

        # Update name if different
        if (
            payload.name
            and payload.name.strip()
            and payload.name.strip() != db_user.name
        ):
            db_user.name = payload.name.strip()
            updated = True

        # Handle password change
        if payload.new_password:
            if not payload.old_password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Old password is required to set a new password",
                )
            # Verify against the database-bound user
            if not db_user.verify_password(payload.old_password):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Old password is incorrect",
                )
            password_hash, salt = User.hash_password(payload.new_password)
            db_user.password_hash = password_hash
            db_user.salt = salt
            updated = True

        if updated:
            session.add(
                db_user
            )  # db_user is already bound to this session, but add() is harmless
            session.commit()
            session.refresh(db_user)

        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
            "updated": updated,
        }


class AdminDeleteUserResource(Resource):
    """
    Admin User Deletion Resource.

    Allows admin to delete user accounts from the system.

    Story Point: SP-ADM-007

    Endpoint: DELETE /admin/users/{user_id}
    Required Role: ROOT
    """

    def delete(
        self,
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a user account by user ID.

        Removes the specified user from the system. Only accessible by ROOT admins.

        Args:
            user_id: ID of the user to be deleted
            current_user: Currently authenticated user dependency
            _: ROOT role verification dependency
            session: Database session dependency

        Returns:
            dict: Confirmation message with keys:
                - message: Success message

        Raises:
            HTTPException: 404 NOT FOUND if user does not exist
                - Detail: "User with ID {user_id} not found"
            HTTPException: 403 FORBIDDEN if user is not ROOT role
        """
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        session.delete(user)
        session.commit()

        return {"message": f"User with ID {user_id} has been deleted successfully."}
