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
from app.middleware import require_employee, require_hr
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


class AllToDoResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all ToDo items of the logged-in user"""

        tasks = session.exec(
            select(ToDo)
            .where(ToDo.user_id == current_user.id)
            .order_by(ToDo.date_created.desc())
        ).all()

        return [
            {
                "id": t.id,
                "task": t.task,
                "status": t.status.value,
                "deadline": t.deadline,
                "date_created": t.date_created,
            }
            for t in tasks
        ]

    def post(
        self,
        data: dict,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Create a new ToDo item"""

        task_text = data.get("task")
        if not task_text:
            raise HTTPException(400, "Task field is required")

        new_task = ToDo(
            user_id=current_user.id,
            task=task_text,
            status=StatusTypeEnum.PENDING,
            deadline=data.get("deadline"),
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return {"message": "Task added successfully", "task_id": new_task.id}


class ToDoResource(Resource):

    def get(
        self,
        task_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get a specific ToDo item"""

        task = session.get(ToDo, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(404, "Task not found")

        return {
            "id": task.id,
            "task": task.task,
            "status": task.status.value,
            "deadline": task.deadline,
            "date_created": task.date_created,
        }

    def put(
        self,
        task_id: int,
        data: dict,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Update a ToDo item"""

        task = session.get(ToDo, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(404, "Task not found")

        if "task" in data:
            task.task = data["task"]

        if "status" in data:
            if data["status"] not in ["pending", "completed"]:
                raise HTTPException(400, "Invalid status")
            task.status = StatusTypeEnum(data["status"])

        if "deadline" in data:
            task.deadline = data["deadline"]

        session.add(task)
        session.commit()
        session.refresh(task)

        return {"message": "Task updated successfully"}

    def delete(
        self,
        task_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Delete a ToDo item"""

        task = session.get(ToDo, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(404, "Task not found")

        session.delete(task)
        session.commit()

        return {"message": "Task deleted successfully"}


class AnnouncementAdminListCreateResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Fetch all announcements"""

        ann_list = session.exec(
            select(Announcement).order_by(Announcement.created_at.desc())
        ).all()

        return [
            {
                "id": a.id,
                "announcement": a.announcement,
                "created_at": a.created_at,
                "user_id": a.user_id,
            }
            for a in ann_list
        ]

    def post(
        self,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Create a new announcement"""

        text = data.get("announcement")
        if not text:
            raise HTTPException(400, "announcement field is required")

        ann = Announcement(
            user_id=current_user.id,
            announcement=text,
        )

        session.add(ann)
        session.commit()
        session.refresh(ann)

        return {"message": "Announcement created", "id": ann.id}


class AnnouncementAdminDetailResource(Resource):

    def get(
        self,
        ann_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Get a specific announcement"""

        ann = session.get(Announcement, ann_id)
        if not ann:
            raise HTTPException(404, "Announcement not found")

        return {
            "id": ann.id,
            "announcement": ann.announcement,
            "created_at": ann.created_at,
            "user_id": ann.user_id,
        }

    def put(
        self,
        ann_id: int,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Update an announcement"""

        ann = session.get(Announcement, ann_id)
        if not ann:
            raise HTTPException(404, "Announcement not found")

        if "announcement" in data:
            ann.announcement = data["announcement"]

        session.commit()
        session.refresh(ann)

        return {"message": "Announcement updated"}

    def delete(
        self,
        ann_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Delete an announcement"""

        ann = session.get(Announcement, ann_id)
        if not ann:
            raise HTTPException(404, "Announcement not found")

        session.delete(ann)
        session.commit()

        return {"message": "Announcement deleted"}


class AnnouncementEmployeeResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Employee: Get their announcements"""

        ann_list = session.exec(
            select(Announcement)
            .where(Announcement.user_id == current_user.id)
            .order_by(Announcement.created_at.desc())
        ).all()

        return [
            {
                "id": a.id,
                "announcement": a.announcement,
                "created_at": a.created_at,
            }
            for a in ann_list
        ]