from logging import getLogger

from app.api.validators import QuickNoteCreate, QuickNoteOut, QuickNoteUpdate
from app.database import QuickNote, User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class AllQuickNotesResource(Resource):
    """
    Employee Quick Notes Management (List/Create) - Core Employee Productivity Feature

    Manages employee personal quick notes. Allows employees to create, retrieve, and manage
    quick notes/memos for personal reference and task tracking. Quick notes serve as a
    lightweight note-taking feature for employees to capture ideas, reminders, and personal
    work notes without formal documentation requirements.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all quick notes for the logged-in employee.

        Returns a collection of all personal quick notes created by the employee,
        enabling quick reference and note organization.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying

        Returns:
            dict: Collection of quick notes
                - notes (list[QuickNoteOut]): Array of quick note objects, each containing:
                    - id (int): Unique note identifier
                    - topic (str): Note topic/title
                    - notes (str): Note content/body

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(500): If database query fails
        """
        try:
            q = select(QuickNote).where(QuickNote.user_id == current_user.id)
            notes = session.exec(q).all()

            return {"notes": [QuickNoteOut.model_validate(n) for n in notes]}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: QuickNoteCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new quick note.

        Allows employees to save quick notes for personal reference. Notes can have an
        optional topic/title for organization, with the main content in the notes field.

        Args:
            payload (QuickNoteCreate): Request payload containing:
                - topic (str, optional): Note topic/title (defaults to "Quick Note")
                - notes (str, required): Note content/body text
            current_user (User): Authenticated employee user object
            session (Session): Database session for persisting note

        Returns:
            dict: Confirmation with note tracking details
                - message (str): "Note saved successfully"
                - id (int): ID of newly created note

        Error Codes:
            - 400 Bad Request: Missing required "notes" field
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database insertion or commit failures

        Raises:
            HTTPException(500): If note creation fails
        """
        try:
            note = QuickNote(
                user_id=current_user.id,
                topic=payload.topic,
                notes=payload.notes,
            )

            session.add(note)
            session.commit()
            session.refresh(note)

            return {"message": "Note saved successfully", "id": note.id}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class QuickNotesResource(Resource):
    """
    Individual Quick Note Operations - Core Employee Productivity Feature

    Handles retrieval, update, and deletion of individual quick notes. Allows employees
    to manage their personal notes independently, including editing topics and content,
    and removing outdated notes.
    """

    def get(
        self,
        note_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve a specific quick note by ID.

        Args:
            note_id (int): The ID of the quick note to retrieve
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Quick note details
                - note (QuickNoteOut): Note object containing:
                    - id (int): Note identifier
                    - topic (str): Note topic/title
                    - notes (str): Note content

        Error Codes:
            - 404 Not Found: Note does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
        """
        note = session.get(QuickNote, note_id)
        if not note or note.user_id != current_user.id:
            raise HTTPException(404, "Note not found")

        return {"note": QuickNoteOut.model_validate(note)}

    def put(
        self,
        note_id: int,
        payload: QuickNoteUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Update a quick note (topic and/or content).

        Allows employees to modify their quick note topic and content. Supports partial
        updates - only provided fields are updated.

        Args:
            note_id (int): The ID of the quick note to update
            payload (QuickNoteUpdate): Update payload with optional fields:
                - topic (str, optional): Updated note topic/title
                - notes (str, optional): Updated note content
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Note updated"

        Error Codes:
            - 404 Not Found: Note does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update or commit failures

        Raises:
            HTTPException(404): If note not found
            HTTPException(500): If database commit fails
        """
        try:
            note = session.get(QuickNote, note_id)
            if not note or note.user_id != current_user.id:
                raise HTTPException(404, "Note not found")

            if payload.topic is not None:
                note.topic = payload.topic
            if payload.notes is not None:
                note.notes = payload.notes

            session.commit()
            session.refresh(note)

            return {"message": "Note updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        note_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a quick note.

        Allows employees to remove quick notes they no longer need. Once deleted,
        the note cannot be recovered.

        Args:
            note_id (int): The ID of the quick note to delete
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Note deleted"

        Error Codes:
            - 404 Not Found: Note does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database deletion or commit failures

        Raises:
            HTTPException(404): If note not found
            HTTPException(500): If database commit fails
        """
        try:
            note = session.get(QuickNote, note_id)
            if not note or note.user_id != current_user.id:
                raise HTTPException(404, "Note not found")

            session.delete(note)
            session.commit()

            return {"message": "Note deleted"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")
