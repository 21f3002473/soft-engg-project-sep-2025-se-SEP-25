from logging import getLogger

from app.agents.employee.rag.qa_chain import get_rag_answer
from app.api.validators import ChatMessage, ChatResponse
from app.database import *
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


def build_employee_context(user: User, session: Session) -> str:
    """Build a rich employee context block for the RAG system."""

    dept_obj = None
    dept_name = None
    if user.department_id:
        dept_obj = session.get(
            type(user).department.property.mapper.class_, user.department_id
        )
        dept_name = dept_obj.name if dept_obj else None

    manager_name = None
    if user.reporting_manager:
        manager = session.get(User, user.reporting_manager)
        manager_name = manager.name if manager else None

    attendance_records = session.exec(
        select(Attendance).where(Attendance.user_id == user.id)
    ).all()

    present = sum(
        1 for a in attendance_records if a.status == AttendanceStatusEnum.PRESENT
    )
    absent = sum(
        1 for a in attendance_records if a.status == AttendanceStatusEnum.ABSENT
    )
    leave = sum(1 for a in attendance_records if a.status == AttendanceStatusEnum.LEAVE)
    remote = sum(
        1 for a in attendance_records if a.status == AttendanceStatusEnum.REMOTE
    )

    todos = session.exec(select(ToDo).where(ToDo.user_id == user.id)).all()
    pending_tasks = [t.task for t in todos if t.status == StatusTypeEnum.PENDING]
    completed_tasks = [t.task for t in todos if t.status == StatusTypeEnum.COMPLETED]

    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user.id)
    ).all()
    assigned_courses = [uc.course.course_name for uc in user_courses if uc.course]
    completed_courses = [
        uc.course.course_name
        for uc in user_courses
        if uc.course and uc.status == StatusTypeEnum.COMPLETED
    ]

    leave_requests = session.exec(select(Leave).where(Leave.user_id == user.id)).all()

    reimbursements = session.exec(
        select(Reimbursement).where(Reimbursement.user_id == user.id)
    ).all()

    return f"""
EMPLOYEE CONTEXT:

IDENTITY:
- Name: {user.name}
- Email: {user.email}
- Role: {user.role}
- Department: {dept_name}
- Reporting Manager: {manager_name}

ATTENDANCE SUMMARY:
- Present: {present}
- Absent: {absent}
- Leave: {leave}
- Remote: {remote}

TASK SUMMARY:
- Pending Tasks: {pending_tasks}
- Completed Tasks: {completed_tasks}

LEARNING SUMMARY:
- Assigned Courses: {assigned_courses}
- Completed Courses: {completed_courses}

LEAVE REQUESTS:
- Total Leave Requests: {len(leave_requests)}

REIMBURSEMENTS:
- Total Claims Submitted: {len(reimbursements)}
"""


class AIAssistantResource(Resource):
    """
    GenAI-Powered HR Chat Assistant Resource — Story Point:
    "As an Employee, I want a GenAI-powered HR assistant that instantly answers my common questions
    so that I don’t need to wait for HR or managers to respond to simple queries."

    This resource provides conversational access to a GenAI HR assistant backed by Google Gemini 2.0 Flash.
    Employees can ask questions related to HR policies, leave processes, company rules, reimbursements,
    WFH guidelines, benefits, dress code, and more.

    Every interaction is **persisted in the Chat model**, enabling:
    - Full conversation history retrieval
    - Consistent user experience across sessions
    - Future context-aware responses (if enabled later)
    - Analytics on employee HR enquires
    """

    async def post(
        self,
        payload: ChatMessage,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Send a user message to the GenAI HR assistant, store the conversation entries (user + assistant),
        and return the AI-generated answer.

        Story Points Supported:
        - "As an Employee, I want instant answers to HR questions about leave, reimbursements,
           company rules, and policies."
        - "As an Employee, I want my chat history saved so I can revisit earlier replies
           and maintain a consistent conversation."

        Workflow:
        1. Save the employee's message to the Chat table.
        2. Construct a Gemini API request with system prompt ("You are Sync'em AI Assistant").
        3. Send the request to Google Gemini 2.0 Flash (30s timeout).
        4. Parse the AI response safely.
        5. Save the AI response to the Chat table.
        6. Return the formatted reply to the frontend.

        Args:
            payload (ChatMessage):
                - message (str): The employee's HR-related question.
                  Example:
                  {
                      "message": "How many casual leaves do we get?"
                  }

            current_user (User):
                Authenticated employee asking the question.

            session (Session):
                Active database session used for storing messages and fetching history.

        Returns:
            ChatResponse:
                - reply (str): AI-generated answer to the employee's query.

        Error Codes:
            - 400 Bad Request:
                * Missing/invalid message in payload.
            - 401 Unauthorized:
                * Employee not authenticated (handled by middleware).
            - 500 Internal Server Error:
                * Gemini API request failure.
                * JSON parsing errors.
                * Database commit issues.
            - 503 Service Unavailable:
                * Gemini service unreachable, heavy load, or timed out.

        Raises:
            HTTPException(500): For LLM failures, unexpected exceptions, or response parsing issues.

        Example Usage:
            POST /assistant
            Body:
            {
                "message": "What is our reimbursement policy?"
            }

            Response:
            {
                "reply": "Employees may claim travel, food, and lodging reimbursements..."
            }
        """

        try:
            user_chat = Chat(
                user_id=current_user.id,
                role="user",
                message=payload.message,
            )
            session.add(user_chat)
            session.commit()
            session.refresh(user_chat)

            employee_context = build_employee_context(current_user, session)

            reply = get_rag_answer(
                user_question=payload.message,
                employee_context=employee_context,
            )

            assistant_chat = Chat(
                user_id=current_user.id,
                role="assistant",
                message=reply,
            )
            session.add(assistant_chat)
            session.commit()

            return ChatResponse(reply=reply)

        except HTTPException:
            raise

        except Exception as e:
            logger.error("AI Assistant Error", exc_info=True)
            raise HTTPException(500, "Internal server error")


class AIChatHistoryResource(Resource):
    """
    Chat History Retrieval Resource — Story Point:
    "As an Employee, I want to view my previous conversations with the HR assistant so that I can
    revisit previous answers without asking the same questions again."

    Provides employees with a complete chronological history of their GenAI HR assistant interactions.
    This improves transparency, user satisfaction, and continuity across sessions.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve the full chat conversation history for the authenticated employee.

        Story Points Supported:
        - "As an Employee, I want my previous HR chatbot interactions accessible so that I can
           continue conversations naturally and reference prior answers."
        - "As an Employee, I want a timeline of all messages exchanged with the assistant."

        Workflow:
        1. Fetch all chat messages for the authenticated user.
        2. Order them chronologically.
        3. Format messages with timestamps, roles, and message content.
        4. Return structured chat history to the client.

        Args:
            current_user (User):
                Authenticated employee whose chat history is being retrieved.

            session (Session):
                Database session for performing the query.

        Returns:
            dict:
                {
                    "messages": [
                        {
                            "id": <int>,
                            "role": "user" | "assistant",
                            "message": <str>,
                            "created_at": <datetime>
                        },
                        ...
                    ]
                }

        Error Codes:
            - 401 Unauthorized:
                * If user is not logged in or not an employee.
            - 500 Internal Server Error:
                * Database query or session failure.

        Raises:
            HTTPException(500): For unexpected database or server failures.

        Example Response:
            {
                "messages": [
                    {
                        "id": 1,
                        "role": "user",
                        "message": "What is the dress code?",
                        "created_at": "2025-01-18T09:22:14Z"
                    },
                    {
                        "id": 2,
                        "role": "assistant",
                        "message": "Our dress code is business casual...",
                        "created_at": "2025-01-18T09:22:15Z"
                    }
                ]
            }
        """

        try:
            chats = session.exec(
                select(Chat)
                .where(Chat.user_id == current_user.id)
                .order_by(Chat.created_at.asc())
            ).all()

            return {
                "messages": [
                    {
                        "id": c.id,
                        "role": c.role,
                        "message": c.message,
                        "created_at": c.created_at,
                    }
                    for c in chats
                ]
            }

        except Exception as e:
            logger.error("Chat History Error", exc_info=True)
            raise HTTPException(500, "Internal server error")
