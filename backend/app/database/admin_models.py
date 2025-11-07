from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import event
from sqlmodel import Field, SQLModel


class SystemLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    log_id: str = Field(index=True, nullable=False, unique=True)
    message: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Backup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    backup_id: str = Field(index=True, nullable=False, unique=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@event.listens_for(Backup, "after_insert", propagate=True)
def log_backup_creation(mapper, connection, target):
    log = SystemLog(
        log_id=f"backup-{target.backup_id}", message="Backup created successfully"
    )
    connection.execute(SystemLog.__table__.insert(), log.dict())
