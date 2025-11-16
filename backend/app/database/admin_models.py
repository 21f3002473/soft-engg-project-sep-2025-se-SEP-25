from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from app.utils import current_utc_time
from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import event
from sqlmodel import Field, SQLModel
from app.utils import current_utc_time


class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    text_log: str = Field(nullable=False)
    time: datetime = Field(default_factory=current_utc_time)


class BackupTypeEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class Backup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: str = Field(nullable=False)
    backup_type: BackupTypeEnum = Field(
        sa_column=Column(
            SQLEnum(BackupTypeEnum, native_enum=False, length=20), nullable=False
        )
    )
    date_time: datetime = Field(default_factory=current_utc_time)


@event.listens_for(Backup, "after_insert", propagate=True)
def log_backup_creation(mapper, connection, target):
    log = Log(
        user_id="admin",
        text_log=f"{target.backup_type.value.capitalize()} backup performed on {target.day}",
    )
    connection.execute(Log.__table__.insert(), log.model_dump())
