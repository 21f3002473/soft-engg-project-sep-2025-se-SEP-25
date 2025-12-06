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
    Story Point: Performance Review Scheduling & Management

    Endpoints:
    - GET  /hr/reviews         -> list all reviews (HR/ROOT)
    - POST /hr/review/create   -> create new review (HR/ROOT)

    Description:
    Manages the complete lifecycle of performance reviews enabling HR managers
    to schedule, create, and track periodic performance reviews for all employees.
    GenAI enhancement allows intelligent scheduling of reviews based on employee
    tenure, role, and performance history for optimal timing and feedback cycles.

    Authorization: Requires HR role

    Returns:
    - 200 OK: Review list or creation confirmation
    - 401 Unauthorized: User not authenticated
    - 403 Forbidden: Insufficient permissions (HR role required)
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all performance reviews from the system.

        Purpose:
        Fetches complete list of performance reviews sorted by creation date.
        Enables HR managers to monitor review cycles, track employee feedback
        history, and ensure consistent performance management across organization.

        Args:
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Returns:
            dict: {"reviews": [review_dict, ...]}
            Each review includes: id, user_id, comments, rating, created_at, modified_at

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 500: Database query error
        """
        reviews = get_all_reviews(session)
        return {"reviews": reviews}

    def post(
        self,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new performance review for an employee.

        Purpose:
        Records performance feedback and ratings as part of periodic review
        cycles. GenAI can optimize review timing based on employee history
        and suggest constructive feedback tailored to employee role.

        Args:
            data: Dictionary containing review fields:
                - user_id (int, required): ID of employee being reviewed
                - rating (int, required): Numerical rating (1-5 scale)
                - comments (str, optional): Reviewer feedback/notes
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Expected Payload:
            {
                "user_id": 5,
                "rating": 4,
                "comments": "Strong technical skills, good team collaboration..."
            }

        Returns:
            dict: {"message": "Review created", "review": review_dict}
            Created review includes: id, user_id, comments, rating, created_at

        Error Codes:
            - 400: Missing required fields (user_id, rating) or invalid rating (not 1-5)
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 404: Target user (employee) not found
            - 500: Database creation error
        """
        review = create_review(data, session)
        return {"message": "Review created", "review": review.dict()}


class HRReviewsByUserResource(Resource):
    """
    Story Point: Performance Review Scheduling & Management

    Endpoint:
    - GET /hr/reviews/{user_id} -> retrieve reviews for a specific employee (HR/ROOT)

    Description:
    Provides access to performance review history for individual employees.
    Enables HR managers to track employee performance trends, identify areas
    for improvement, and plan targeted development or review follow-ups.

    Authorization: Requires HR role
    """

    def get(
        self,
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all performance reviews for a specific employee.

        Purpose:
        Fetches complete performance history for an employee sorted by
        review date. Enables HR managers to analyze performance trends,
        prepare for upcoming reviews, and track improvement over time.

        Args:
            user_id: ID of the employee to retrieve reviews for
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Returns:
            dict: {"reviews": [review_dict, ...]}
            Reviews sorted by created_at descending (newest first)
            Each review includes: id, user_id, comments, rating, created_at, modified_at

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 500: Database query error

        Note:
            Returns empty list if employee has no reviews yet (not an error).
        """
        reviews = get_reviews_by_user(user_id, session)
        return {"reviews": [r.dict() for r in reviews]}


class HRReviewDetailResource(Resource):
    """
    Story Point: Performance Review Scheduling & Management

    Endpoints:
    - PUT /hr/review/{review_id}     -> update existing review (HR/ROOT)
    - DELETE /hr/review/{review_id}  -> remove review (ROOT only)

    Description:
    Provides detailed operations on individual reviews. Enables modification
    of feedback and corrections, as well as removal of reviews when needed.
    GenAI can suggest review improvements or flag inconsistent ratings.

    Authorization:
    - PUT: Requires HR role (modify reviews)
    - DELETE: Requires Root role (remove reviews - high security)
    """

    def put(
        self,
        review_id: int,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Update an existing performance review.

        Purpose:
        Allows HR managers to correct review data or update feedback comments
        as part of the review refinement process. Supports partial updates
        to modify individual fields independently.

        Args:
            review_id: ID of the review to update
            data: Dictionary containing fields to update (optional):
                - rating (int): Updated rating (1-5 scale)
                - comments (str): Updated feedback/notes
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Expected Payload (partial update allowed):
            {
                "rating": 5,
                "comments": "Exceptional performance and leadership..."
            }

        Returns:
            dict: {"message": "Review updated", "review": review_dict}
            Updated review includes: id, user_id, comments, rating, modified_at

        Error Codes:
            - 400: Invalid rating (not in 1-5 range) or empty payload
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 404: Review with review_id not found
            - 500: Database update error
        """
        review = update_review(review_id, data, session)
        return {"message": "Review updated", "review": review.dict()}

    def delete(
        self,
        review_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a performance review from the system.

        Purpose:
        Removes reviews from the database (typically in case of data errors
        or test records). Only Root users can delete reviews to maintain
        audit compliance and prevent loss of valid performance history.

        Args:
            review_id: ID of the review to delete
            current_user: Authenticated user making the request
            _: Authorization check ensuring Root role
            session: Database session for query execution

        Returns:
            dict: {"message": "Review deleted"}

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (Root role required)
            - 404: Review with review_id not found
            - 500: Database deletion error

        Warning:
            This operation is irreversible. Deleted reviews cannot be recovered.
        """
        return delete_review(review_id, session)
