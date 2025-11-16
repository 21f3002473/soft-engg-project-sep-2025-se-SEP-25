from logging import getLogger

from app.api.validators import FAQCreate, FAQOut
from app.database import FAQ, User, get_session
from app.middleware import require_employee, require_hr
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class HRFAQCreateResource(Resource):
    """
    HR FAQ Creation Resource - Story Point:
    "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

    Allows HR personnel to create and publish FAQ entries. This resource enables HR to build a
    self-service knowledge base of frequently asked questions covering HR policies, benefits,
    procedures, and other common employee inquiries. Employees can then access these FAQs
    independently without needing to contact HR directly.
    """

    def post(
        self,
        payload: FAQCreate,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new FAQ entry (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Allows HR to add new questions and answers to the FAQ database. This builds the
        self-service knowledge base that employees can search and browse to find answers
        independently, reducing HR support overhead.

        Args:
            payload (FAQCreate): Request payload containing:
                - question (str, required): The FAQ question text
                - answer (str, required): The corresponding answer/response
            current_user (User): Authenticated HR user object (verified by require_hr middleware)
            session (Session): Database session for storing the FAQ

        Returns:
            dict: Confirmation with newly created FAQ details
                - message (str): "FAQ created successfully"
                - id (int): ID of the newly created FAQ entry

        Error Codes:
            - 400 Bad Request: Invalid or missing question/answer in payload
            - 401 Unauthorized: User is not HR personnel (caught by middleware)
            - 500 Internal Server Error: Database insertion or commit failures

        Raises:
            HTTPException(500): If database operation fails during creation or commit
        """
        try:
            faq = FAQ(question=payload.question, answer=payload.answer)
            session.add(faq)
            session.commit()
            session.refresh(faq)
            return {"message": "FAQ created successfully", "id": faq.id}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class HRFAQDetailResource(Resource):
    """
    FAQ Detail Operations Resource - Story Point:
    "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

    Handles retrieval, update, and deletion of individual FAQ entries. Employees can view FAQs,
    while HR can modify or remove outdated entries. Supports the full FAQ lifecycle management
    and enables employees to access specific FAQ answers on-demand.
    """

    def get(
        self,
        faq_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve a specific FAQ entry by ID (Employee access).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Args:
            faq_id (int): The ID of the FAQ entry to retrieve
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: FAQ data wrapped in response
                - faq (FAQOut): FAQ object containing:
                    - id (int): FAQ identifier
                    - question (str): The question text
                    - answer (str): The answer text

        Error Codes:
            - 404 Not Found: FAQ with given ID does not exist
            - 401 Unauthorized: User is not an employee (caught by middleware)

        Raises:
            HTTPException(404): If FAQ ID is not found in database
        """
        faq = session.get(FAQ, faq_id)
        if not faq:
            raise HTTPException(404, "FAQ not found")

        return {"faq": FAQOut.model_validate(faq)}

    def put(
        self,
        faq_id: int,
        payload: FAQCreate,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Update an existing FAQ entry (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Allows HR to modify FAQ questions or answers when policies change, clarifications are needed,
        or incorrect information needs to be corrected. Updated FAQs are immediately available
        to all employees browsing the FAQ database.

        Args:
            faq_id (int): The ID of the FAQ to update
            payload (FAQCreate): Request payload containing:
                - question (str): Updated question text
                - answer (str): Updated answer text
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "FAQ updated successfully"

        Error Codes:
            - 404 Not Found: FAQ with given ID does not exist
            - 400 Bad Request: Invalid or missing question/answer in payload
            - 401 Unauthorized: User is not HR personnel
            - 500 Internal Server Error: Database commit failures

        Raises:
            HTTPException(404): If FAQ ID not found
            HTTPException(500): If database update fails
        """
        try:
            faq = session.get(FAQ, faq_id)
            if not faq:
                raise HTTPException(404, "FAQ not found")

            faq.question = payload.question
            faq.answer = payload.answer

            session.commit()
            return {"message": "FAQ updated successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        faq_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Delete an FAQ entry (HR only).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Allows HR to remove outdated, irrelevant, or incorrect FAQs from the knowledge base.
        Deleted FAQs will no longer be visible to employees.

        Args:
            faq_id (int): The ID of the FAQ to delete
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "FAQ deleted successfully"

        Error Codes:
            - 404 Not Found: FAQ with given ID does not exist
            - 401 Unauthorized: User is not HR personnel
            - 500 Internal Server Error: Database deletion or commit failures

        Raises:
            HTTPException(404): If FAQ ID not found
            HTTPException(500): If database deletion fails
        """
        try:
            faq = session.get(FAQ, faq_id)
            if not faq:
                raise HTTPException(404, "FAQ not found")

            session.delete(faq)
            session.commit()
            return {"message": "FAQ deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class HRFAQListEmployeeResource(Resource):
    """
    Employee FAQ Browsing Resource - Story Point:
    "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

    Provides employees with access to the complete FAQ database. This enables self-service
    knowledge discovery, allowing employees to find answers to common HR questions (policies,
    benefits, procedures, leave, etc.) without having to contact HR directly or wait for
    manager assistance. Supports immediate, independent resolution of frequent inquiries.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all FAQ entries (Employee access).

        Story Points Supported:
        - "As an Employee, I want to browse HR FAQs and documents so that I can find answers without waiting for HR responses."

        Workflow:
        1. Fetch all FAQ entries from database
        2. Validate and serialize to FAQOut format
        3. Return complete FAQ list to employee

        This enables employees to browse the entire FAQ knowledge base, search through questions,
        and find answers to HR-related queries without manager or HR intervention. Supports
        immediate self-service resolution of common questions about dress code, leave policies,
        WFH guidelines, travel reimbursement, benefits, etc.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Collection of FAQs
                - faqs (list[FAQOut]): Array of FAQ objects, each containing:
                    - id (int): FAQ identifier
                    - question (str): The question text
                    - answer (str): The answer text

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(500): If database query fails
        """
        try:
            faqs = session.exec(select(FAQ)).all()
            return {"faqs": [FAQOut.model_validate(faq) for faq in faqs]}
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")
