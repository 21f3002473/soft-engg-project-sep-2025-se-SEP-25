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


# ============================================
# AI-POWERED TEAM ALLOCATION MODELS
# ============================================


class AllocationPolicyTypeEnum(str, Enum):
    MAX_PROJECTS_PER_EMPLOYEE = "max_projects_per_employee"
    MAX_WORKLOAD_HOURS = "max_workload_hours"
    DEPARTMENT_BALANCE = "department_balance"
    SKILL_DIVERSITY = "skill_diversity"
    EXPERIENCE_MIX = "experience_mix"
    MANDATORY_ROLES = "mandatory_roles"


class AllocationPolicy(SQLModel, table=True):
    """Company-defined rules for team allocation"""

    id: Optional[int] = Field(default=None, primary_key=True)
    policy_name: str = Field(index=True, nullable=False)
    policy_type: AllocationPolicyTypeEnum = Field(
        sa_column=Column(
            SQLEnum(AllocationPolicyTypeEnum, native_enum=False, length=50),
            nullable=False,
        )
    )
    policy_config: str = Field(
        description="JSON configuration for the policy (e.g., {'max_projects': 3})"
    )
    is_active: bool = Field(default=True)
    priority: int = Field(
        default=1, description="Higher number = higher priority in conflicts"
    )
    created_at: datetime = Field(default_factory=current_utc_time)
    updated_at: datetime = Field(default_factory=current_utc_time)


class ProjectRequirementAnalysis(SQLModel, table=True):
    """GenAI analysis of project requirements"""

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    analysis_date: datetime = Field(default_factory=current_utc_time)

    # AI-extracted requirements
    required_skills: str = Field(
        description="JSON array of required skills with proficiency levels"
    )
    experience_level_needed: str = Field(
        description="JSON object with min/preferred experience levels"
    )
    estimated_team_size: int = Field(default=0)
    estimated_duration_weeks: Optional[int] = Field(default=None)
    complexity_score: Optional[float] = Field(
        default=None, description="AI-calculated complexity (0-100)"
    )

    # Team composition recommendations
    recommended_roles: str = Field(
        description="JSON array of roles needed (e.g., frontend, backend, tester)"
    )
    workload_estimate_hours: Optional[float] = Field(default=None)

    # AI analysis metadata
    ai_model_used: str = Field(default="groq/llama-3.3-70b-versatile")
    analysis_confidence: Optional[float] = Field(
        default=None, description="Confidence score (0-1)"
    )
    raw_analysis_text: Optional[str] = Field(
        default=None, description="Full AI analysis for reference"
    )

    project: Optional["Project"] = Relationship()


class AllocationRecommendationStatusEnum(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_ASSIGNED = "auto_assigned"
    EXPIRED = "expired"


class AllocationRecommendation(SQLModel, table=True):
    """AI-generated employee allocation recommendations"""

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False)
    employee_id: int = Field(foreign_key="user.id", nullable=False)

    # Recommendation metadata
    recommendation_date: datetime = Field(default_factory=current_utc_time)
    status: AllocationRecommendationStatusEnum = Field(
        default=AllocationRecommendationStatusEnum.PENDING_REVIEW,
        sa_column=Column(
            SQLEnum(AllocationRecommendationStatusEnum, native_enum=False, length=30),
            nullable=False,
        ),
    )

    # Scoring and reasoning
    match_score: float = Field(
        description="Overall match score (0-100), higher is better"
    )
    skill_match_score: float = Field(default=0.0)
    experience_match_score: float = Field(default=0.0)
    availability_score: float = Field(default=0.0)
    workload_score: float = Field(default=0.0)

    # Explainable AI reasoning
    reasoning: str = Field(description="Human-readable explanation for recommendation")
    matching_skills: str = Field(
        description="JSON array of employee skills matching project needs"
    )
    concerns: Optional[str] = Field(
        default=None, description="JSON array of potential concerns or risks"
    )

    # Policy compliance
    policy_violations: Optional[str] = Field(
        default=None, description="JSON array of policy violations if any"
    )
    policy_compliance_score: float = Field(
        default=100.0, description="Compliance score (0-100)"
    )

    # Assignment details
    proposed_role: Optional[str] = Field(default=None)
    proposed_allocation_percentage: Optional[float] = Field(
        default=100.0, description="% of employee time allocated to this project"
    )

    # Feedback and learning
    feedback_provided: bool = Field(default=False)
    feedback_text: Optional[str] = Field(default=None)
    feedback_date: Optional[datetime] = Field(default=None)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = Field(default=None)

    # AI metadata
    ai_model_version: str = Field(default="v1.0")
    recommendation_generation_time_ms: Optional[int] = Field(default=None)

    project: Optional["Project"] = Relationship()
    employee: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AllocationRecommendation.employee_id]"}
    )
    reviewer: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AllocationRecommendation.reviewed_by]"}
    )


class AllocationQuery(SQLModel, table=True):
    """Natural language queries from managers"""

    id: Optional[int] = Field(default=None, primary_key=True)
    query_text: str = Field(description="Natural language query from manager")
    query_date: datetime = Field(default_factory=current_utc_time)
    queried_by: int = Field(foreign_key="user.id", nullable=False)

    # Query processing
    interpreted_intent: Optional[str] = Field(
        default=None, description="AI interpretation of query intent"
    )
    extracted_parameters: Optional[str] = Field(
        default=None, description="JSON of extracted parameters (skills, project, etc.)"
    )

    # Response
    response_text: Optional[str] = Field(
        default=None, description="Natural language response from AI"
    )
    response_data: Optional[str] = Field(
        default=None, description="JSON structured response data"
    )
    response_time_ms: Optional[int] = Field(default=None)

    # Related entities
    related_project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    recommended_employees: Optional[str] = Field(
        default=None, description="Comma-separated employee IDs"
    )

    queried_by_user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AllocationQuery.queried_by]"}
    )
    related_project: Optional["Project"] = Relationship()


class EmployeeSkill(SQLModel, table=True):
    """Employee skills for matching"""

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="user.id", nullable=False)
    skill_name: str = Field(index=True, nullable=False)
    proficiency_level: str = Field(
        description="beginner, intermediate, advanced, expert"
    )
    years_of_experience: Optional[float] = Field(default=None)

    # Verification
    verified: bool = Field(default=False)
    verified_by: Optional[int] = Field(default=None, foreign_key="user.id")
    verified_at: Optional[datetime] = Field(default=None)

    # Metadata
    added_at: datetime = Field(default_factory=current_utc_time)
    last_used_at: Optional[datetime] = Field(default=None)

    employee: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EmployeeSkill.employee_id]"}
    )
    verifier: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EmployeeSkill.verified_by]"}
    )


class EmployeeAvailability(SQLModel, table=True):
    """Track employee availability and current workload"""

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="user.id", nullable=False, index=True)

    # Current workload
    current_projects_count: int = Field(default=0)
    current_workload_hours_per_week: float = Field(
        default=0.0, description="Total hours allocated per week"
    )
    max_capacity_hours_per_week: float = Field(
        default=40.0, description="Maximum working hours per week"
    )

    # Availability
    is_available: bool = Field(default=True)
    availability_start_date: Optional[datetime] = Field(default=None)
    unavailability_reason: Optional[str] = Field(default=None)

    # Updated tracking
    last_updated: datetime = Field(default_factory=current_utc_time)
    updated_by: Optional[int] = Field(default=None, foreign_key="user.id")

    employee: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EmployeeAvailability.employee_id]"}
    )
    updater: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EmployeeAvailability.updated_by]"}
    )

