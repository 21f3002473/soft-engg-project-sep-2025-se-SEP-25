# app/controllers/hr/hr_review_controller.py
from typing import Any, Dict, List

from app.database import User
from app.database.hr_models import PerformanceReview
from fastapi import HTTPException
from sqlmodel import Session, select


def get_all_reviews(session: Session) -> List[PerformanceReview]:
    return session.exec(
        select(PerformanceReview).order_by(PerformanceReview.created_at.desc())
    ).all()


def get_reviews_by_user(user_id: int, session: Session) -> List[PerformanceReview]:
    return session.exec(
        select(PerformanceReview)
        .where(PerformanceReview.user_id == user_id)
        .order_by(PerformanceReview.created_at.desc())
    ).all()


def create_review(payload: Dict[str, Any], session: Session) -> PerformanceReview:
    # payload: {'user_id': int, 'comments': str (opt), 'rating': int}
    # validate target user exists:
    user = session.get(User, payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    review = PerformanceReview(
        user_id=payload["user_id"],
        comments=payload.get("comments"),
        rating=payload["rating"],
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def update_review(
    review_id: int, payload: Dict[str, Any], session: Session
) -> PerformanceReview:
    review = session.get(PerformanceReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if "comments" in payload:
        review.comments = payload["comments"]
    if "rating" in payload:
        review.rating = payload["rating"]

    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def delete_review(review_id: int, session: Session) -> dict:
    review = session.get(PerformanceReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    session.delete(review)
    session.commit()
    return {"message": "Review deleted"}
