import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from app.config import Config
from app.utils import current_utc_time
from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    email: str = Field(
        index=True,
    )
    name: str = Field(
        index=True,
        nullable=False,
    )
    password_hash: str = Field(
        index=False,
        nullable=False,
    )
    salt: str = Field(default_factory=lambda: secrets.token_hex(16), nullable=False)
    role: str = Field(
        default="employee",
        index=True,
        nullable=False,
    )

    department_id: Optional[int] = Field(default=None, foreign_key="department.id")
    reporting_manager: Optional[int] = Field(default=None, foreign_key="users.id")
    img_base64: Optional[str] = Field(default=None)

    attendances: list["Attendance"] = Relationship(back_populates="user")

    department: Optional["Department"] = Relationship(back_populates="users")
    managed_departments: List["Department"] = Relationship(back_populates="manager")

    requests: list["Request"] = Relationship(back_populates="user")
    leaves: list["Leave"] = Relationship(back_populates="user")
    reimbursements: list["Reimbursement"] = Relationship(back_populates="user")
    transfer_requests: list["TransferRequest"] = Relationship(back_populates="user")
    todos: list["ToDo"] = Relationship(back_populates="user")
    user_courses: list["UserCourse"] = Relationship(back_populates="user")
    announcements: list["Announcement"] = Relationship(back_populates="user")

    performance_reviews: list["PerformanceReview"] = Relationship(back_populates="user")

    managed_projects: List["Project"] = Relationship(back_populates="manager")
    emp_todos: List["EmpTodo"] = Relationship(back_populates="user")
    updates: List["Update"] = Relationship(back_populates="created_by_user")
    user_projects: List["UserProject"] = Relationship(back_populates="user")

    def generate_token(self) -> str:

        expiry = int(time.time()) + 86400
        token_data = f"{self.id}:{self.email}:{expiry}"
        signature = hmac.new(
            Config.SECRET_KEY.encode(), token_data.encode(), hashlib.sha256
        ).hexdigest()
        return f"{token_data}:{signature}"

    def verify_password(self, password: str) -> bool:
        password_hash = hashlib.sha256(f"{password}{self.salt}".encode()).hexdigest()
        return hmac.compare_digest(self.password_hash, password_hash)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:

        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return password_hash, salt


class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    REMOTE = "remote"


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    date: datetime = Field(default_factory=lambda: current_utc_time().date())
    check_in: Optional[datetime] = Field(default=None)
    check_out: Optional[datetime] = Field(default=None)
    status: AttendanceStatusEnum = Field(default=AttendanceStatusEnum.PRESENT)
    worked_hours: Optional[float] = Field(default=None)
    remarks: Optional[str] = Field(default=None)

    user: Optional["Users"] = Relationship(back_populates="attendances")


class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    manager_id: Optional[int] = Field(default=None, foreign_key="users.id")

    manager: Optional["User"] = Relationship(back_populates="managed_departments")
    users: List["User"] = Relationship(back_populates="department")


class RequestTypeEnum(str, Enum):
    LEAVE = "leave"
    REIMBURSEMENT = "reimbursement"
    TRANSFER = "transfer"


class StatusTypeEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class Request(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_type: RequestTypeEnum = Field(nullable=False)
    status: StatusTypeEnum = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id")

    created_date: datetime = Field(default_factory=current_utc_time)
    modified_date: datetime = Field(default_factory=current_utc_time)

    leave_id: Optional[int] = Field(default=None, foreign_key="leave.id")
    reimbursement_id: Optional[int] = Field(
        default=None, foreign_key="reimbursement.id"
    )
    transfer_id: Optional[int] = Field(default=None, foreign_key="transferrequest.id")

    user: "User" = Relationship(back_populates="requests")
    leave: Optional["Leave"] = Relationship(back_populates="request")
    reimbursement: Optional["Reimbursement"] = Relationship(back_populates="request")
    transfer: Optional["TransferRequest"] = Relationship(back_populates="request")


@event.listens_for(Request, "before_update", propagate=True)
def update_modified_date(mapper, connection, target):
    target.modified_date = datetime.now(timezone.utc)


class Leave(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    leave_type: str = Field(nullable=False)
    from_date: datetime = Field(nullable=False)
    to_date: datetime = Field(nullable=False)
    reason: Optional[str] = Field(default=None)

    request_id: Optional[int] = Field(default=None, foreign_key="request.id")

    user: Optional["User"] = Relationship(back_populates="leaves")
    request: Optional["Request"] = Relationship(back_populates="leave")


class Reimbursement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    expense_type: str = Field(nullable=False)
    amount: float = Field(nullable=False)
    date_expense: datetime = Field(nullable=False)
    remark: Optional[str] = Field(default=None)

    request_id: Optional[int] = Field(default=None, foreign_key="request.id")

    user: Optional["User"] = Relationship(back_populates="reimbursements")
    request: Optional["Request"] = Relationship(back_populates="reimbursement")


class TransferRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    current_department: str = Field(nullable=False)
    request_department: str = Field(nullable=False)
    reason: Optional[str] = Field(default=None)

    request_id: Optional[int] = Field(default=None, foreign_key="request.id")

    user: Optional["User"] = Relationship(back_populates="transfer_requests")
    request: Optional["Request"] = Relationship(back_populates="transfer")


class QuickNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str = Field(nullable=False)
    notes: str = Field(nullable=False)


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_name: str = Field(nullable=False)
    course_link: Optional[str] = Field(default=None)
    topics: Optional[str] = Field(default=None)

    user_courses: List["UserCourse"] = Relationship(back_populates="course")


class UserCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="course.id")
    status: StatusTypeEnum = Field(nullable=False)

    user: Optional["User"] = Relationship(back_populates="user_courses")
    course: Optional["Course"] = Relationship(back_populates="user_courses")


class ToDo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    task: str = Field(nullable=False)
    status: StatusTypeEnum = Field(nullable=False)
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="todos")


class Announcement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    announcement: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="announcements")
