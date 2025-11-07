from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.utils import current_utc_time
from sqlmodel import Field, Relationship, SQLModel


class StatusTypeEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True, unique=True, nullable=False)
    client_name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    detail_base64: Optional[str] = Field(
        default=None, description="Client detail encoded in Base64"
    )

    projects: List["Project"] = Relationship(back_populates="client")
    requirements: List["Requirement"] = Relationship(back_populates="client")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True, unique=True, nullable=False)
    project_name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: StatusTypeEnum = Field(default=StatusTypeEnum.IN_PROGRESS)
    client_id: int = Field(foreign_key="client.id", nullable=False)
    manager_id: Optional[int] = Field(foreign_key="user.id")

    manager: Optional["User"] = Relationship(back_populates="managed_projects")
    client: Optional["Client"] = Relationship(back_populates="projects")
    requirements: List["Requirement"] = Relationship(back_populates="project")
    updates: List["Update"] = Relationship(back_populates="project")
    emp_todos: List["EmpTodo"] = Relationship(back_populates="project")
    user_projects: List["UserProject"] = Relationship(back_populates="project")


class UserProject(SQLModel, table=True):
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )

    user: Optional["User"] = Relationship(back_populates="user_projects")
    project: Optional["Project"] = Relationship(back_populates="user_projects")


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True, unique=True, nullable=False)
    requirements: str = Field(nullable=False)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    client_id: int = Field(foreign_key="client.id", nullable=False)

    project: Optional["Project"] = Relationship(back_populates="requirements")
    client: Optional["Client"] = Relationship(back_populates="requirements")
    emp_todos: List["EmpTodo"] = Relationship(back_populates="requirement")


class Update(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    update_id: str = Field(index=True, unique=True, nullable=False)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    created_by: Optional[int] = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=current_utc_time)
    details: Optional[str] = Field(default=None)

    created_by_user: Optional["User"] = Relationship(back_populates="updates")
    project: Optional["Project"] = Relationship(back_populates="updates")


class EmpTodo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: int = Field(foreign_key="requirement.id", nullable=False)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    client_id: Optional[int] = Field(foreign_key="client.id", nullable=True)
    status: StatusTypeEnum = Field(default=StatusTypeEnum.PENDING)
    weightage: float = Field(default=0.0)
    user_id: Optional[int] = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="emp_todos")
    project: Optional["Project"] = Relationship(back_populates="emp_todos")
    requirement: Optional["Requirement"] = Relationship(back_populates="emp_todos")
