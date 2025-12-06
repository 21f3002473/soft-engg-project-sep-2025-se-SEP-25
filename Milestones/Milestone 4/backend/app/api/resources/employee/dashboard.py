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
    """
    Employee Dashboard Resource - Story Point: "As an Employee, I want to browse HR FAQs and documents...

    Provides a consolidated dashboard view for employees displaying:
    - Personal task statistics (pending/completed)
    - Request tracking (leave, reimbursement, transfer)
    - Course completion progress
    - Personal to-do items
    - Recent HR announcements

    This resource aggregates key employee information for quick overview without
    waiting for individual API calls. Supports performance tracking and proactive improvements.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve complete dashboard data for logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents..." (announcement section)
        - "As an Employee, I want to submit leave and reimbursement requests..." (request tracking)
        - "As an Employee, I want to search for and view learning courses..." (courses_completed count)

        Args:
            current_user (User): Authenticated employee user object (via require_employee middleware)
            session (Session): Database session for querying

        Returns:
            dict: Dashboard data containing:
                - message (str): Success confirmation
                - stats (dict): Aggregated counts
                    - pending_tasks (int): Count of pending to-do items
                    - completed_tasks (int): Count of completed to-do items
                    - requests (int): Total requests (leave/reimbursement/transfer) submitted
                    - courses_completed (int): Count of completed courses
                - tasks (list[dict]): Employee's recent to-do items with id, task, status, deadline, date_created
                - announcements (list[dict]): Latest 10 HR announcements (id, announcement, created_at)
                - user (dict): Current user profile (id, name, email, role)

        Error Codes:
            - 500 Internal Server Error: Database query failures, invalid session state

        Raises:
            HTTPException(500): If any database operation fails during aggregation
        """

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
    """
    Employee To-Do Management Resource - Story Point: "As an Employee, I want to browse HR FAQs and documents..."

    Manages employee personal to-do items. Allows employees to create, retrieve, and track
    personal tasks and deadlines. This enables employees to organize work priorities and
    monitor task completion status independently.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all to-do items for the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests..." (task tracking)

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            list[dict]: Array of to-do items, each containing:
                - id (int): Unique task identifier
                - task (str): Task description
                - status (str): Either "pending" or "completed"
                - deadline (datetime): Optional task deadline
                - date_created (datetime): When task was created

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
        """

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
        """
        Create a new to-do item for the employee.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests..." (task management)

        Args:
            data (dict): Request payload containing:
                - task (str, required): Description of the task
                - deadline (datetime, optional): Optional deadline for the task
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message with newly created task ID
                - message (str): "Task added successfully"
                - task_id (int): ID of the newly created to-do item

        Error Codes:
            - 400 Bad Request: Missing required "task" field
            - 401 Unauthorized: User is not an employee
        """

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
    """
    Individual To-Do Item Resource - Story Point: "As an Employee, I want to browse HR FAQs and documents..."

    Handles CRUD operations on individual to-do items. Ensures employees can only modify
    their own tasks. Supports task status updates and deadline modifications.
    """

    def get(
        self,
        task_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific to-do item.

        Args:
            task_id (int): The ID of the to-do item to retrieve
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: To-do item details
                - id (int): Task identifier
                - task (str): Task description
                - status (str): "pending" or "completed"
                - deadline (datetime): Optional deadline
                - date_created (datetime): Creation timestamp

        Error Codes:
            - 404 Not Found: Task does not exist or belongs to another user
            - 401 Unauthorized: User is not an employee
        """

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
        """
        Update a specific to-do item (task description, status, or deadline).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests..." (status tracking)

        Args:
            task_id (int): The ID of the to-do item to update
            data (dict): Request payload with optional fields:
                - task (str, optional): Updated task description
                - status (str, optional): Must be "pending" or "completed"
                - deadline (datetime, optional): Updated deadline
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Task updated successfully"

        Error Codes:
            - 404 Not Found: Task does not exist or belongs to another user
            - 400 Bad Request: Invalid status value (not "pending" or "completed")
            - 401 Unauthorized: User is not an employee
        """

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
        """
        Delete a specific to-do item.

        Args:
            task_id (int): The ID of the to-do item to delete
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Task deleted successfully"

        Error Codes:
            - 404 Not Found: Task does not exist or belongs to another user
            - 401 Unauthorized: User is not an employee
        """

        task = session.get(ToDo, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(404, "Task not found")

        session.delete(task)
        session.commit()

        return {"message": "Task deleted successfully"}


class AnnouncementAdminListCreateResource(Resource):
    """
    HR Announcement Management (List/Create) - Story Point: "As an Employee, I want to browse HR FAQs and documents..."

    Allows HR personnel to create and retrieve all announcements. Announcements are
    broadcast communications to all employees about policies, updates, and HR-related
    information. This supports the employee story of browsing HR documents and staying
    informed on organizational changes.
    """

    def get(
        self,
        user_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all announcements (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents..." (announcement retrieval)

        Args:
            user_id (int): HR user ID making the request (for audit purposes)
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            list[dict]: Array of all announcements, each containing:
                - id (int): Announcement identifier
                - announcement (str): Announcement content/text
                - created_at (datetime): When announcement was created
                - user_id (int): HR user who created it

        Error Codes:
            - 401 Unauthorized: User is not HR personnel (caught by middleware)
        """

        ann_list = session.exec(
            select(Announcement).order_by(Announcement.created_at.desc())
        ).all()

        return [
            {
                "id": a.id,
                "announcement": a.announcement,
                "created_at": a.created_at,
                "user_id": user_id,
            }
            for a in ann_list
        ]

    def post(
        self,
        user_id: int,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new announcement (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents..." (announcement creation)

        Args:
            user_id (int): HR user ID creating the announcement
            data (dict): Request payload containing:
                - announcement (str, required): Announcement text/content
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation with announcement details
                - message (str): "Announcement created"
                - id (int): ID of newly created announcement

        Error Codes:
            - 400 Bad Request: Missing required "announcement" field
            - 401 Unauthorized: User is not HR personnel
        """

        text = data.get("announcement")
        if not text:
            raise HTTPException(400, "announcement field is required")

        ann = Announcement(
            user_id=user_id,
            announcement=text,
        )

        session.add(ann)
        session.commit()
        session.refresh(ann)

        return {"message": "Announcement created", "id": ann.id}


class AnnouncementAdminDetailResource(Resource):
    """
    HR Announcement Detail Operations - Story Point: "As an Employee, I want to browse HR FAQs and documents..."

    Handles retrieval, update, and deletion of individual announcements by HR personnel.
    Enables HR to manage announcement lifecycle and correct or retract information.
    """

    def get(
        self,
        ann_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve a specific announcement by ID (HR only).

        Args:
            ann_id (int): The ID of the announcement to retrieve
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Announcement details
                - id (int): Announcement identifier
                - announcement (str): Announcement content
                - created_at (datetime): Creation timestamp
                - user_id (int): HR user who created it

        Error Codes:
            - 404 Not Found: Announcement with given ID does not exist
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Update an existing announcement (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents..." (announcement updates)

        Args:
            ann_id (int): The ID of the announcement to update
            data (dict): Request payload with optional fields:
                - announcement (str, optional): Updated announcement text
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Announcement updated"

        Error Codes:
            - 404 Not Found: Announcement does not exist
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Delete an announcement (HR only).

        Args:
            ann_id (int): The ID of the announcement to delete
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Announcement deleted"

        Error Codes:
            - 404 Not Found: Announcement does not exist
            - 401 Unauthorized: User is not HR personnel
        """

        ann = session.get(Announcement, ann_id)
        if not ann:
            raise HTTPException(404, "Announcement not found")

        session.delete(ann)
        session.commit()

        return {"message": "Announcement deleted"}


class AnnouncementEmployeeResource(Resource):
    """
    Employee Announcement Viewing - Story Point: "As an Employee, I want to browse HR FAQs and documents..."

    Read-only endpoint for employees to view HR announcements. Enables employees to stay
    informed about organizational policies, updates, and HR-related information without
    waiting for manager notifications. Part of the self-service HR information browsing feature.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all announcements for the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            list[dict]: Array of announcements, each containing:
                - id (int): Announcement identifier
                - announcement (str): Announcement content/text
                - created_at (datetime): When announcement was published

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
        """

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
