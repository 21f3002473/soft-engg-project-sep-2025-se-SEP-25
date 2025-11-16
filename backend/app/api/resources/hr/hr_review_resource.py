# app/api/resources/hr/hr_review_resource.py
from typing import Any

from app.controllers import get_current_active_user
from app.controllers.hr.hr_review_controller import (
    create_review,
    delete_review,
    get_all_reviews,
    get_reviews_by_user,
    update_review,
)
from app.database import User, get_session
from app.middleware import require_hr, require_root
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session


class HRReviewsListResource(Resource):
    """
    GET  /hr/reviews            -> list all (HR/ROOT)
    POST /hr/review/create     -> create (HR/ROOT)
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        reviews = get_all_reviews(session)
        return {"reviews": [r.dict() for r in reviews]}

    def post(
        self,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        review = create_review(data, session)
        return {"message": "Review created", "review": review.dict()}


class HRReviewsByUserResource(Resource):
    """
    GET /hr/reviews/{user_id} -> reviews for a given user (HR/ROOT)
    """

    def get(
        self,
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        reviews = get_reviews_by_user(user_id, session)
        return {"reviews": [r.dict() for r in reviews]}


class HRReviewDetailResource(Resource):
    """
    PUT /hr/review/{review_id}
    DELETE /hr/review/{review_id}
    """

    def put(
        self,
        review_id: int,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        review = update_review(review_id, data, session)
        return {"message": "Review updated", "review": review.dict()}

    def delete(
        self,
        review_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        return delete_review(review_id, session)
