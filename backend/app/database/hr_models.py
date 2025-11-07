from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


class PerformanceReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    comments: Optional[str] = Field(default=None)
    rating: int = Field(ge=1, le=5, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="performance_reviews")
    
@event.listens_for(PerformanceReview, "before_update", propagate=True)
def update_review_timestamp(mapper, connection, target):
    target.modified_at = datetime.now(timezone.utc)


class HRPolicy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
