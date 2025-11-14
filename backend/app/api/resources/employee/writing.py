from logging import getLogger

from app.api.validators import QuickNoteCreate, QuickNoteOut, QuickNoteUpdate
from app.database import QuickNote, User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class QuickNotesResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all quick notes for the user"""
        try:
            q = select(QuickNote).where(QuickNote.user_id == current_user.id)
            notes = session.exec(q).all()

            return {"notes": [QuickNoteOut.from_orm(n) for n in notes]}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: QuickNoteCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Create a new quick note"""
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

    def put(
        self,
        note_id: int,
        payload: QuickNoteUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Update a quick note"""
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
        """Delete a quick note"""
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
