from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True, unique=True, nullable=False)
    client_name: str = Field(nullable=False)

    projects: List["Project"] = Relationship(back_populates="client")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True, unique=True, nullable=False)
    project_name: str = Field(nullable=False)
    status: str = Field(default="ongoing")
    client_id: int = Field(foreign_key="client.id", nullable=False)

    client: Optional["Client"] = Relationship(back_populates="projects")
    manager: Optional["Users"] = Relationship(back_populates="managed_projects")
    requirements: List["Requirement"] = Relationship(back_populates="project")
    assigned_users: List["Users"] = Relationship(
        back_populates="assigned_projects", link_model="ProjectUserLink"
    )


class ProjectUser(SQLModel, table=True):
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True, unique=True, nullable=False)
    description: str = Field(nullable=False)
    project_id: int = Field(foreign_key="project.id", nullable=False)

    project: Optional["Project"] = Relationship(back_populates="requirements")
