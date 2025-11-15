from logging import getLogger

from app.api.validators import AccountOut, AccountUpdate
from app.database import Department, User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session

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
                dept_name = dept.name if dept else None

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

        except Exception:
            logger.error("Account GET error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        payload: AccountUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        try:
            update_data = payload.model_dump(exclude_unset=True)

            user = session.merge(current_user)

            for key, value in update_data.items():
                setattr(user, key, value)

            session.commit()
            session.refresh(user)

            return {"message": "Account updated successfully"}

        except Exception:
            logger.error("Account Update error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        current_user: User = Depends(require_employee()),
    ):
        """Client-side token delete — endpoint is symbolic."""
        return {"message": "Logged out successfully"}