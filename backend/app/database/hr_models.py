from datetime import datetime, timezone
from typing import Optional

from app.utils import current_utc_time
from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


class PerformanceReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    comments: Optional[str] = Field(default=None)
    rating: int = Field(ge=1, le=5, nullable=False)
    created_at: datetime = Field(default_factory=current_utc_time)
    modified_at: datetime = Field(default_factory=current_utc_time)

    user: Optional["User"] = Relationship(back_populates="performance_reviews")


@event.listens_for(PerformanceReview, "before_update", propagate=True)
def update_review_timestamp(mapper, connection, target):
    target.modified_at = current_utc_time()


class HRPolicy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=current_utc_time)
