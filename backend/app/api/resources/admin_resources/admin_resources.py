from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from app.controllers import get_current_active_user
from app.database import User, get_session
from app.database.admin_models import Backup, BackupTypeEnum, Log
from app.middleware import Role, can_view_system_logs, require_root
from fastapi import Depends, HTTPException, Query, status
from fastapi_restful import Resource
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

# -----------------------------
# Validators / Schemas
# -----------------------------


class AdminRegistrationValidator(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class AdminAddEmployeeValidator(BaseModel):
    name: str = Field(min_length=1)
    role: str = Field(
        description="Role name such as 'HR', 'Product Manager', or 'Employee'"
    )
    email: Optional[EmailStr] = None


class BackupItem(BaseModel):
    day: str
    type: str = Field(pattern="^(full|incremental|differential)$")
    datetime: datetime


class BackupConfigPayload(BaseModel):
    backups: List[BackupItem]


class AccountUpdatePayload(BaseModel):
    name: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None


# -----------------------------
# Helpers
# -----------------------------


def _normalize_role(role_in: str) -> str:
    """Map friendly role names to internal Role enum values."""
    value = role_in.strip().lower()
    mapping = {
        "hr": Role.HUMAN_RESOURCE.value,
        "human resource": Role.HUMAN_RESOURCE.value,
        "human_resource": Role.HUMAN_RESOURCE.value,
        "product manager": Role.PRODUCT_MANAGER.value,
        "product_manager": Role.PRODUCT_MANAGER.value,
        "pm": Role.PRODUCT_MANAGER.value,
        "employee": Role.EMPLOYEE.value,
        "root": Role.ROOT.value,
        # allow passing raw values too
        Role.HUMAN_RESOURCE.value: Role.HUMAN_RESOURCE.value,
        Role.PRODUCT_MANAGER.value: Role.PRODUCT_MANAGER.value,
        Role.EMPLOYEE.value: Role.EMPLOYEE.value,
        Role.ROOT.value: Role.ROOT.value,
    }
    if value not in mapping:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown role '{role_in}'. Expected one of HR, Product Manager, Employee",
        )
    return mapping[value]


def _backup_type_from_str(value: str) -> BackupTypeEnum:
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
    """Register a new Admin (ROOT) user.

    POST /admin/register
    Body: { name, email, password }
    Success: 201 with user summary
    """

    def post(
        self,
        payload: AdminRegistrationValidator,
        session: Session = Depends(get_session),
    ):
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
            role=Role.ROOT.value,
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
    """System summary stats for Admin dashboard.

    GET /admin/summary
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
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
    """Manage employees (create/list).

    GET /admin/employees
    POST /admin/employees
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
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
    """View and update backup configuration.

    GET /admin/backup-config
    PUT /admin/backup-config
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
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
        # Replace existing configuration
        existing = session.exec(select(Backup)).all()
        for item in existing:
            session.delete(item)
        session.commit()

        for item in payload.backups:
            backup = Backup(
                day=item.day,
                backup_type=_backup_type_from_str(item.type),
                date_time=item.datetime,
            )
            session.add(backup)
        session.commit()

        return {
            "message": "Backup configuration updated",
            "count": len(payload.backups),
        }


class AdminLogsResource(Resource):
    """System logs listing.

    GET /admin/logs?limit=50&offset=0
    """

    def get(
        self,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(can_view_system_logs()),
        session: Session = Depends(get_session),
    ):
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
    """Software update status (placeholder). GET /admin/updates"""

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
    ):
        return {
            "currentVersion": "1.0.0",
            "updateAvailable": False,
            "lastChecked": datetime.utcnow().isoformat() + "Z",
        }


class AdminAccountResource(Resource):
    """Admin account info and updates.

    GET /admin/account
    PUT /admin/account
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
    ):
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
        updated = False

        if (
            payload.name
            and payload.name.strip()
            and payload.name.strip() != current_user.name
        ):
            current_user.name = payload.name.strip()
            updated = True

        if payload.new_password:
            if not payload.old_password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Old password is required to set a new password",
                )
            if not current_user.verify_password(payload.old_password):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Old password is incorrect",
                )
            password_hash, salt = User.hash_password(payload.new_password)
            current_user.password_hash = password_hash
            current_user.salt = salt
            updated = True

        if updated:
            session.add(current_user)
            session.commit()
            session.refresh(current_user)

        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "updated": updated,
        }
