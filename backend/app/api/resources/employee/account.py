from logging import getLogger
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

from app.database import get_session, User
from app.middleware import require_employee
from app.database import Department
from app.api.validators import AccountUpdate, AccountOut

logger = getLogger(__name__)


class AccountResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        try:
            dept_name = None
            if current_user.department_id:
                dept = session.get(Department, current_user.department_id)
                if dept:
                    dept_name = dept.name

            return AccountOut(
                id=current_user.id,
                name=current_user.name,
                email=current_user.email,
                role=current_user.role,
                department_id=current_user.department_id,
                reporting_manager=current_user.reporting_manager,
                img_base64=current_user.img_base64,
                department_name=dept_name,
            )

        except Exception as e:
            logger.error("Account GET error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        payload: AccountUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        try:
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(current_user, key, value)

            session.add(current_user)
            session.commit()
            session.refresh(current_user)

            return {"message": "Account updated successfully"}

        except Exception as e:
            logger.error("Account Update error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        current_user: User = Depends(require_employee()),
    ):
        """Client-side will delete token; this endpoint just confirms"""
        return {"message": "Logged out successfully"}
