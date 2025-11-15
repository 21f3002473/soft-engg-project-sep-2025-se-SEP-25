from logging import getLogger

from app.database import (
    Announcement,
    Request,
    StatusTypeEnum,
    ToDo,
    User,
    UserCourse,
    get_session,
)
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, func, select

logger = getLogger(__name__)


class DashboardResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):

        try:
            user_id = current_user.id

            pending_count = session.exec(
                select(func.count())
                .select_from(ToDo)
                .where(ToDo.user_id == user_id)
                .where(ToDo.status == StatusTypeEnum.PENDING)
            ).one()

            completed_count = session.exec(
                select(func.count())
                .select_from(ToDo)
                .where(ToDo.user_id == user_id)
                .where(ToDo.status == StatusTypeEnum.COMPLETED)
            ).one()

            req_count = session.exec(
                select(func.count())
                .select_from(Request)
                .where(Request.user_id == user_id)
            ).one()

            courses_completed = session.exec(
                select(func.count())
                .select_from(UserCourse)
                .where(UserCourse.user_id == user_id)
                .where(UserCourse.status == StatusTypeEnum.COMPLETED)
            ).one()

            tasks = session.exec(
                select(ToDo)
                .where(ToDo.user_id == user_id)
                .order_by(ToDo.date_created.desc())
            ).all()

            task_list = [
                {
                    "id": t.id,
                    "task": t.task,
                    "status": t.status.value,
                    "deadline": t.deadline,
                    "date_created": t.date_created,
                }
                for t in tasks
            ]

            announcements = session.exec(
                select(Announcement).order_by(Announcement.created_at.desc()).limit(10)
            ).all()

            announcement_list = [
                {
                    "id": a.id,
                    "announcement": a.announcement,
                    "created_at": a.created_at,
                }
                for a in announcements
            ]

            return {
                "message": "Dashboard data retrieved successfully",
                "stats": {
                    "pending_tasks": pending_count,
                    "completed_tasks": completed_count,
                    "requests": req_count,
                    "courses_completed": courses_completed,
                },
                "tasks": task_list,
                "announcements": announcement_list,
                "user": {
                    "id": current_user.id,
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": current_user.role,
                },
            }

        except Exception as e:
            logger.error(f"Dashboard error: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")
