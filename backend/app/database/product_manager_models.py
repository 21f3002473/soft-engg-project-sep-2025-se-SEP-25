from datetime import datetime
from email.mime import image
from enum import Enum
from typing import List, Optional

from app.utils import current_utc_time
from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel


class StatusTypeEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True, unique=True, nullable=False)
    client_name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    image_base64: Optional[str] = Field(
        default=None, description="Client detail encoded in Base64"
    )

    projects: List["Project"] = Relationship(back_populates="client")
    requirements: List["Requirement"] = Relationship(back_populates="client")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True, unique=True, nullable=False)
    project_name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: StatusTypeEnum = Field(
        default=StatusTypeEnum.PENDING,
        sa_column=Column(SQLEnum(StatusTypeEnum, native_enum=False, length=20)),
    )
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
        default=None, foreign_key="user.id", primary_key=True
    )

    user: Optional["User"] = Relationship(back_populates="user_projects")
    project: Optional["Project"] = Relationship(back_populates="user_projects")


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True, unique=True, nullable=False)
    requirements: str = Field(nullable=False)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    client_id: int = Field(foreign_key="client.id", nullable=False)
    status: StatusTypeEnum = Field(
        default=StatusTypeEnum.PENDING,
        sa_column=Column(SQLEnum(StatusTypeEnum, native_enum=False, length=20)),
    )

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
    status: StatusTypeEnum = Field(
        default=StatusTypeEnum.PENDING,
        sa_column=Column(SQLEnum(StatusTypeEnum, native_enum=False, length=20)),
    )
    weightage: float = Field(default=0.0)
    user_id: Optional[int] = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="emp_todos")
    project: Optional["Project"] = Relationship(back_populates="emp_todos")
    requirement: Optional["Requirement"] = Relationship(back_populates="emp_todos")


class RequirementRoadmap(SQLModel, table=True):
    """
    Database model to store AI-generated roadmaps for project requirements.
    Tracks the execution plan, milestones, and workflow updates.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, index=True)
    client_id: int = Field(foreign_key="client.id", nullable=False, index=True)

    generated_at: datetime = Field(default_factory=current_utc_time)
    generated_by: Optional[int] = Field(foreign_key="user.id")
    trigger_type: str = Field(
        default="manual",
        description="manual, requirement_added, requirement_updated, status_change",
    )

    roadmap_data: str = Field(description="JSON string containing the full roadmap")
    summary: Optional[str] = Field(
        default=None, description="AI-generated summary of the roadmap"
    )
    estimated_completion_days: Optional[int] = Field(default=None)

    is_current: bool = Field(
        default=True, description="Whether this is the current active roadmap"
    )
    version: int = Field(default=1, description="Roadmap version number")

    email_sent: bool = Field(default=False)
    email_sent_at: Optional[datetime] = Field(default=None)


class ClientProgressEmail(SQLModel, table=True):
    """
    Database model to track all progress emails sent to clients.
    Stores AI-generated email content and tracking information.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, index=True)
    client_id: int = Field(foreign_key="client.id", nullable=False, index=True)

    sent_at: datetime = Field(default_factory=current_utc_time, index=True)
    sent_by: Optional[int] = Field(foreign_key="user.id")
    trigger_type: str = Field(
        default="manual", description="manual, update_added, milestone_completed, etc."
    )

    subject: str = Field(description="Email subject line")
    email_body_text: str = Field(description="Plain text email body")
    email_body_html: str = Field(description="HTML formatted email body")

    recipient_email: str = Field(description="Client email address")
    cc_emails: Optional[str] = Field(
        default=None, description="Comma-separated CC emails"
    )

    delivery_status: str = Field(default="sent", description="sent, failed, pending")
    opened: bool = Field(default=False, description="Whether email was opened")
    opened_at: Optional[datetime] = Field(default=None)

    update_ids: Optional[str] = Field(
        default=None, description="Comma-separated update IDs included in email"
    )
    project_status: Optional[str] = Field(
        default=None, description="Project status at time of email"
    )


class ProjectDailyReport(SQLModel, table=True):
    """
    Database model to store daily AI-generated progress reports for projects.
    Automatically generated every day to track project progress, blockers, and achievements.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, index=True)
    client_id: int = Field(foreign_key="client.id", nullable=False, index=True)

    report_date: datetime = Field(default_factory=current_utc_time, index=True)
    generated_at: datetime = Field(default_factory=current_utc_time)
    trigger_type: str = Field(
        default="scheduled", description="scheduled, manual, on_demand"
    )

    summary: str = Field(description="Brief summary of daily progress")
    achievements: Optional[str] = Field(
        default=None, description="JSON array of achievements"
    )
    blockers: Optional[str] = Field(
        default=None, description="JSON array of blockers/issues"
    )
    upcoming_tasks: Optional[str] = Field(
        default=None, description="JSON array of planned tasks"
    )
    metrics: Optional[str] = Field(
        default=None, description="JSON object with progress metrics"
    )

    report_body_text: str = Field(description="Plain text full report")
    report_body_html: str = Field(description="HTML formatted full report")

    email_sent: bool = Field(default=False)
    email_sent_at: Optional[datetime] = Field(default=None)
    recipient_email: Optional[str] = Field(default=None)
    email_delivery_status: str = Field(
        default="pending", description="pending, sent, failed"
    )

    updates_count: int = Field(
        default=0, description="Number of updates in this period"
    )
    completion_percentage: Optional[float] = Field(
        default=None, description="Project completion %"
    )

    update_ids_included: Optional[str] = Field(
        default=None, description="Comma-separated update IDs covered"
    )
    project_status_snapshot: Optional[str] = Field(
        default=None, description="Project status at report time"
    )


class EmployeeDailyReport(SQLModel, table=True):
    """
    Database model to store daily AI-generated performance reports for employees.
    Tracks employee performance across all assigned projects and tasks.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="user.id", nullable=False, index=True)

    report_date: datetime = Field(default_factory=current_utc_time, index=True)
    generated_at: datetime = Field(default_factory=current_utc_time)
    trigger_type: str = Field(
        default="scheduled", description="scheduled, manual, on_demand"
    )

    summary: str = Field(description="Brief summary of daily performance")
    achievements: Optional[str] = Field(
        default=None, description="JSON array of achievements"
    )
    challenges: Optional[str] = Field(
        default=None, description="JSON array of challenges faced"
    )
    recommendations: Optional[str] = Field(
        default=None, description="JSON array of improvement recommendations"
    )
    focus_areas: Optional[str] = Field(
        default=None, description="JSON array of areas to focus on"
    )

    report_body_text: str = Field(description="Plain text full report")
    report_body_html: str = Field(description="HTML formatted full report")

    tasks_completed_today: int = Field(
        default=0, description="Tasks completed in last 24h"
    )
    tasks_in_progress: int = Field(default=0, description="Tasks currently in progress")
    projects_worked_on: int = Field(
        default=0, description="Number of projects worked on"
    )
    overall_completion_rate: Optional[float] = Field(
        default=None, description="Overall task completion %"
    )
    productivity_score: Optional[float] = Field(
        default=None, description="AI-calculated productivity score (0-100)"
    )

    project_contributions: Optional[str] = Field(
        default=None,
        description="JSON object mapping project_id to contribution details",
    )

    email_sent: bool = Field(default=False)
    email_sent_at: Optional[datetime] = Field(default=None)
    recipient_email: Optional[str] = Field(default=None)
    email_delivery_status: str = Field(
        default="pending", description="pending, sent, failed"
    )

    task_ids_included: Optional[str] = Field(
        default=None, description="Comma-separated task IDs covered"
    )
