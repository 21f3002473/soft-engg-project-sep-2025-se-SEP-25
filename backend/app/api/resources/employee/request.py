from logging import getLogger

from app.api.validators import LeaveCreate, ReimbursementCreate, TransferCreate
from app.database import (
    Leave,
    Reimbursement,
    Request,
    RequestTypeEnum,
    StatusTypeEnum,
    Transfer,
    User,
    get_session,
)
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class LeaveRequestResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all leave requests made by the user"""
        try:
            q = (
                select(Leave, Request)
                .join(Request, Request.leave_id == Leave.id)
                .where(Leave.user_id == current_user.id)
                .order_by(Request.created_date.desc())
            )
            rows = session.exec(q).all()

            data = []
            for leave, req in rows:
                data.append(
                    {
                        "request_id": req.id,
                        "leave_id": leave.id,
                        "leave_type": leave.leave_type,
                        "from_date": leave.from_date,
                        "to_date": leave.to_date,
                        "reason": leave.reason,
                        "status": req.status.value,
                        "created_date": req.created_date,
                    }
                )

            return {"leaves": data}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: LeaveCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Submit new leave request"""
        try:
            leave = Leave(
                user_id=current_user.id,
                leave_type=payload.leave_type,
                from_date=payload.from_date,
                to_date=payload.to_date,
                reason=payload.reason,
            )
            session.add(leave)
            session.commit()
            session.refresh(leave)

            req = Request(
                request_type=RequestTypeEnum.LEAVE,
                status=StatusTypeEnum.PENDING,
                user_id=current_user.id,
                leave_id=leave.id,
            )
            session.add(req)
            session.commit()
            session.refresh(req)

            return {"message": "Leave request submitted", "request_id": req.id}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        leave_id: int,
        payload: LeaveCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Update an existing leave request (only if pending)"""

        try:
            leave = session.get(Leave, leave_id)
            if not leave or leave.user_id != current_user.id:
                raise HTTPException(404, "Leave request not found")

            req = session.exec(
                select(Request).where(Request.leave_id == leave_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be modified")

            leave.leave_type = payload.leave_type
            leave.from_date = payload.from_date
            leave.to_date = payload.to_date
            leave.reason = payload.reason

            session.add(leave)
            session.commit()
            session.refresh(leave)

            return {"message": "Leave request updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        leave_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Delete a leave request (only if pending)"""

        try:
            leave = session.get(Leave, leave_id)
            if not leave or leave.user_id != current_user.id:
                raise HTTPException(404, "Leave request not found")

            req = session.exec(
                select(Request).where(Request.leave_id == leave_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be deleted")

            session.delete(req)
            session.delete(leave)
            session.commit()

            return {"message": "Leave request deleted"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class ReimbursementRequestResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all reimbursement requests"""
        try:
            q = (
                select(Reimbursement, Request)
                .join(Request, Request.reimbursement_id == Reimbursement.id)
                .where(Reimbursement.user_id == current_user.id)
            )
            rows = session.exec(q).all()

            data = []
            for rmb, req in rows:
                data.append(
                    {
                        "request_id": req.id,
                        "reimbursement_id": rmb.id,
                        "expense_type": rmb.expense_type,
                        "amount": rmb.amount,
                        "date_expense": rmb.date_expense,
                        "remark": rmb.remark,
                        "status": req.status.value,
                    }
                )

            return {"reimbursements": data}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: ReimbursementCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Submit reimbursement request"""
        try:
            rb = Reimbursement(
                user_id=current_user.id,
                expense_type=payload.expense_type,
                amount=payload.amount,
                date_expense=payload.date_expense,
                remark=payload.remark,
            )
            session.add(rb)
            session.commit()
            session.refresh(rb)

            req = Request(
                request_type=RequestTypeEnum.REIMBURSEMENT,
                status=StatusTypeEnum.PENDING,
                user_id=current_user.id,
                reimbursement_id=rb.id,
            )
            session.add(req)
            session.commit()
            session.refresh(req)

            return {"message": "Reimbursement request submitted"}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        reimbursement_id: int,
        payload: ReimbursementCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Update reimbursement request (only pending)"""
        try:
            rb = session.get(Reimbursement, reimbursement_id)
            if not rb or rb.user_id != current_user.id:
                raise HTTPException(404, "Reimbursement not found")

            req = session.exec(
                select(Request).where(Request.reimbursement_id == reimbursement_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be modified")

            rb.expense_type = payload.expense_type
            rb.amount = payload.amount
            rb.date_expense = payload.date_expense
            rb.remark = payload.remark

            session.commit()

            return {"message": "Reimbursement updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        reimbursement_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Delete reimbursement request (only pending)"""
        try:
            rb = session.get(Reimbursement, reimbursement_id)
            if not rb or rb.user_id != current_user.id:
                raise HTTPException(404, "Reimbursement not found")

            req = session.exec(
                select(Request).where(Request.reimbursement_id == reimbursement_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be deleted")

            session.delete(req)
            session.delete(rb)
            session.commit()

            return {"message": "Reimbursement deleted"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class TransferRequestResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Get all transfer requests"""
        try:
            q = (
                select(Transfer, Request)
                .join(Request, Request.transfer_id == Transfer.id)
                .where(Transfer.user_id == current_user.id)
            )
            rows = session.exec(q).all()

            data = []
            for tr, req in rows:
                data.append(
                    {
                        "request_id": req.id,
                        "transfer_id": tr.id,
                        "current_department": tr.current_department,
                        "request_department": tr.request_department,
                        "reason": tr.reason,
                        "status": req.status.value,
                    }
                )

            return {"transfers": data}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: TransferCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Submit transfer request"""
        try:
            tr = Transfer(
                user_id=current_user.id,
                current_department=payload.current_department,
                request_department=payload.request_department,
                reason=payload.reason,
            )
            session.add(tr)
            session.commit()
            session.refresh(tr)

            req = Request(
                request_type=RequestTypeEnum.TRANSFER,
                status=StatusTypeEnum.PENDING,
                user_id=current_user.id,
                transfer_id=tr.id,
            )
            session.add(req)
            session.commit()

            return {"message": "Transfer request submitted"}

        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        transfer_id: int,
        payload: TransferCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Update transfer request (only pending)"""
        try:
            tr = session.get(Transfer, transfer_id)
            if not tr or tr.user_id != current_user.id:
                raise HTTPException(404, "Transfer request not found")

            req = session.exec(
                select(Request).where(Request.transfer_id == transfer_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be modified")

            tr.current_department = payload.current_department
            tr.request_department = payload.request_department
            tr.reason = payload.reason

            session.commit()

            return {"message": "Transfer request updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        transfer_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Delete transfer request (only pending)"""
        try:
            tr = session.get(Transfer, transfer_id)
            if not tr or tr.user_id != current_user.id:
                raise HTTPException(404, "Transfer request not found")

            req = session.exec(
                select(Request).where(Request.transfer_id == transfer_id)
            ).first()

            if req.status != StatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be deleted")

            session.delete(req)
            session.delete(tr)
            session.commit()

            return {"message": "Transfer request deleted"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")
