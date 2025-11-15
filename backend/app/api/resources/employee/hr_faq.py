from logging import getLogger

from app.api.validators import FAQCreate, FAQOut
from app.database import FAQ, User, get_session
from app.middleware import require_employee, require_hr
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class HRFAQCreateResource(Resource):

    def post(
        self,
        payload: FAQCreate,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Create FAQ"""
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

    def get(
        self,
        faq_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Employee: Get a single FAQ"""
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
        """HR: Update FAQ"""
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
        """HR: Delete FAQ"""
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

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all HR FAQs"""
        try:
            faqs = session.exec(select(FAQ)).all()
            return {"faqs": [FAQOut.model_validate(faq) for faq in faqs]}
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")