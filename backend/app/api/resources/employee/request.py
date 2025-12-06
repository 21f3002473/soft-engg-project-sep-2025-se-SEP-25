from logging import getLogger
from typing import Optional

from app.api.validators import LeaveCreate, ReimbursementCreate, TransferCreate
from app.database import (
    Leave,
    Reimbursement,
    Request,
    RequestStatusTypeEnum,
    RequestTypeEnum,
    Transfer,
    User,
    get_session,
)
from app.middleware import require_employee, require_hr
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class AllLeaveRequestResource(Resource):
    """
    Employee Leave Request Management (List/Create) - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Manages leave request lifecycle. Allows employees to view all their submitted leave requests
    and create new leave requests. Tracks request status (pending/completed) to provide visibility
    into the approval process. Enables employees to efficiently manage time-off requests without
    manual HR coordination.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all leave requests submitted by the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Returns all leave requests (pending and completed) in reverse chronological order
        (newest first). Includes full request details and current status for tracking.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying

        Returns:
            dict: Collection of leave requests
                - leaves (list[dict]): Array of leave requests, each containing:
                    - request_id (int): Unique request identifier
                    - leave_id (int): Leave record identifier
                    - leave_type (str): Type of leave (e.g., "Annual", "Sick", "Casual")
                    - from_date (datetime): Leave start date
                    - to_date (datetime): Leave end date
                    - reason (str, optional): Reason for leave
                    - status (str): "pending" or "completed"
                    - created_date (datetime): When request was submitted

        Error Codes:
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(500): If database query fails
        """
        try:
            q = (
                select(Leave, Request)
                .join(Request, Request.leave_id == Leave.id)
                .where(Leave.user_id == current_user.id)
                .order_by(Request.created_date.desc())
            )
            rows = session.exec(q).all()

            data = [
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
                for leave, req in rows
            ]

            return {"leaves": data}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: LeaveCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Submit a new leave request.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Creates a leave request record and initializes it with "pending" status. The request
        is now visible in the employee's request tracker and available for HR review/approval.

        Args:
            payload (LeaveCreate): Request payload containing:
                - leave_type (str, required): Type of leave (e.g., "Annual", "Sick", "Casual")
                - from_date (datetime, required): Leave start date
                - to_date (datetime, required): Leave end date
                - reason (str, optional): Reason for the leave request
            current_user (User): Authenticated employee user object
            session (Session): Database session for persisting request

        Returns:
            dict: Confirmation with request tracking details
                - message (str): "Leave request submitted"
                - request_id (int): ID to track this request

        Error Codes:
            - 400 Bad Request: Invalid dates or missing required fields
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database insertion or commit failures

        Raises:
            HTTPException(500): If leave creation or request creation fails
        """
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
                status=RequestStatusTypeEnum.PENDING,
                user_id=current_user.id,
                leave_id=leave.id,
            )
            session.add(req)
            session.commit()

            return {
                "message": "Leave request submitted",
                "request_id": req.id,
                "leave_id": leave.id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class LeaveRequestResource(Resource):
    """
    Individual Leave Request Operations - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Handles retrieval, update, and deletion of individual leave requests. Employees can only
    modify requests that are still in "pending" status, allowing for correction before approval.
    Once approved/completed, requests are locked from modification.
    """

    def get(
        self,
        leave_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific leave request.

        Args:
            leave_id (int): The ID of the leave request to retrieve
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Leave request details
                - request_id (int): Unique request identifier
                - leave_id (int): Leave record identifier
                - leave_type (str): Type of leave
                - from_date (datetime): Leave start date
                - to_date (datetime): Leave end date
                - reason (str, optional): Reason for leave
                - status (str): "pending" or "completed"

        Error Codes:
            - 404 Not Found: Leave request does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures
        """
        try:
            leave = session.get(Leave, leave_id)
            if not leave or leave.user_id != current_user.id:
                raise HTTPException(404, "Leave request not found")

            req = session.exec(
                select(Request).where(Request.leave_id == leave_id)
            ).first()

            return {
                "request_id": req.id,
                "leave_id": leave.id,
                "leave_type": leave.leave_type,
                "from_date": leave.from_date,
                "to_date": leave.to_date,
                "reason": leave.reason,
                "status": req.status.value,
            }

        except HTTPException:
            raise
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
        """
        Update a leave request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to modify leave request details before submission/approval. Once a
        request is approved (completed), it cannot be modified.

        Args:
            leave_id (int): The ID of the leave request to update
            payload (LeaveCreate): Updated request payload with:
                - leave_type (str): Updated leave type
                - from_date (datetime): Updated start date
                - to_date (datetime): Updated end date
                - reason (str, optional): Updated reason
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Leave request updated"

        Error Codes:
            - 404 Not Found: Leave request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending" (cannot modify approved requests)
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If leave request not found
            HTTPException(500): If database commit fails
        """
        try:
            leave = session.get(Leave, leave_id)
            print(leave)
            if not leave or leave.user_id != current_user.id:
                raise HTTPException(404, "Leave request not found")

            req = session.exec(
                select(Request).where(Request.leave_id == leave_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be modified")

            leave.leave_type = payload.leave_type
            leave.from_date = payload.from_date
            leave.to_date = payload.to_date
            leave.reason = payload.reason

            session.commit()

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
        """
        Delete a leave request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to withdraw pending leave requests. Once approved, requests cannot
        be deleted and must go through cancellation workflow.

        Args:
            leave_id (int): The ID of the leave request to delete
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Leave request deleted"

        Error Codes:
            - 404 Not Found: Leave request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending" (cannot delete approved requests)
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database deletion failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If leave request not found
            HTTPException(500): If database commit fails
        """
        try:
            leave = session.get(Leave, leave_id)
            if not leave or leave.user_id != current_user.id:
                raise HTTPException(404, "Leave request not found")

            req = session.exec(
                select(Request).where(Request.leave_id == leave_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
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


class AllReimbursementRequestResource(Resource):
    """
    Employee Reimbursement Request Management (List/Create) - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Manages reimbursement request lifecycle. Allows employees to track all submitted reimbursement
    requests and create new ones. Enables employees to efficiently document and track expense
    reimbursement submissions and approvals.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all reimbursement requests submitted by the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Returns all reimbursement requests (pending and completed) with full expense details
        and current approval status.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying

        Returns:
            dict: Collection of reimbursement requests
                - reimbursements (list[dict]): Array of reimbursement records, each containing:
                    - request_id (int): Unique request identifier
                    - reimbursement_id (int): Reimbursement record identifier
                    - expense_type (str): Type of expense (e.g., "Travel", "Meals", "Hotel")
                    - amount (float): Reimbursement amount
                    - date_expense (datetime): When the expense occurred
                    - remark (str, optional): Additional notes
                    - status (str): "pending" or "completed"

        Error Codes:
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(500): If database query fails
        """
        try:
            q = (
                select(Reimbursement, Request)
                .join(Request, Request.reimbursement_id == Reimbursement.id)
                .where(Reimbursement.user_id == current_user.id)
            )
            rows = session.exec(q).all()

            data = [
                {
                    "request_id": req.id,
                    "reimbursement_id": rmb.id,
                    "expense_type": rmb.expense_type,
                    "amount": rmb.amount,
                    "date_expense": rmb.date_expense,
                    "remark": rmb.remark,
                    "status": req.status.value,
                }
                for rmb, req in rows
            ]

            return {"reimbursements": data}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: ReimbursementCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Submit a new reimbursement request.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Creates a reimbursement request record with "pending" status. The request is now
        tracked in the system and available for HR/manager review and approval.

        Args:
            payload (ReimbursementCreate): Request payload containing:
                - expense_type (str, required): Type of expense (e.g., "Travel", "Meals", "Hotel")
                - amount (float, required): Reimbursement amount claimed
                - date_expense (datetime, required): When the expense occurred
                - remark (str, optional): Additional notes/description
            current_user (User): Authenticated employee user object
            session (Session): Database session for persisting request

        Returns:
            dict: Confirmation message
                - message (str): "Reimbursement submitted"

        Error Codes:
            - 400 Bad Request: Invalid amount or missing required fields
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database insertion or commit failures

        Raises:
            HTTPException(500): If reimbursement creation fails
        """
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
                status=RequestStatusTypeEnum.PENDING,
                user_id=current_user.id,
                reimbursement_id=rb.id,
            )
            session.add(req)
            session.commit()

            return {
                "message": "Reimbursement submitted",
                "request_id": req.id,
                "reimbursement_id": rb.id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class ReimbursementRequestResource(Resource):
    """
    Individual Reimbursement Request Operations - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Handles retrieval, update, and deletion of individual reimbursement requests. Employees can
    only modify requests that are still "pending", allowing for expense correction before approval.
    """

    def get(
        self,
        reimbursement_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific reimbursement request.

        Args:
            reimbursement_id (int): The ID of the reimbursement request to retrieve
            current_user (User): Authenticated employee user object
            session: Database session

        Returns:
            dict: Reimbursement request details
                - request_id (int): Unique request identifier
                - reimbursement_id (int): Reimbursement record identifier
                - expense_type (str): Type of expense
                - amount (float): Reimbursement amount
                - date_expense (datetime): When expense occurred
                - remark (str, optional): Additional notes
                - status (str): "pending" or "completed"

        Error Codes:
            - 404 Not Found: Reimbursement request does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures
        """
        try:
            rb = session.get(Reimbursement, reimbursement_id)
            if not rb or rb.user_id != current_user.id:
                raise HTTPException(404, "Reimbursement not found")

            req = session.exec(
                select(Request).where(Request.reimbursement_id == reimbursement_id)
            ).first()

            return {
                "request_id": req.id,
                "reimbursement_id": rb.id,
                "expense_type": rb.expense_type,
                "amount": rb.amount,
                "date_expense": rb.date_expense,
                "remark": rb.remark,
                "status": req.status.value,
            }

        except HTTPException:
            raise
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
        """
        Update a reimbursement request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to modify reimbursement details before approval. Once approved,
        requests are locked from modification.

        Args:
            reimbursement_id (int): The ID of the reimbursement request to update
            payload (ReimbursementCreate): Updated request payload with:
                - expense_type (str): Updated expense type
                - amount (float): Updated amount
                - date_expense (datetime): Updated expense date
                - remark (str, optional): Updated notes
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Reimbursement updated"

        Error Codes:
            - 404 Not Found: Reimbursement request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending" (cannot modify approved requests)
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If reimbursement not found
            HTTPException(500): If database commit fails
        """
        try:
            rb = session.get(Reimbursement, reimbursement_id)
            if not rb or rb.user_id != current_user.id:
                raise HTTPException(404, "Reimbursement not found")

            req = session.exec(
                select(Request).where(Request.reimbursement_id == reimbursement_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
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
        """
        Delete a reimbursement request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to withdraw pending reimbursement requests. Once approved, requests
        cannot be deleted.

        Args:
            reimbursement_id (int): The ID of the reimbursement request to delete
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Reimbursement deleted"

        Error Codes:
            - 404 Not Found: Reimbursement request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending" (cannot delete approved requests)
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database deletion failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If reimbursement not found
            HTTPException(500): If database commit fails
        """
        try:
            rb = session.get(Reimbursement, reimbursement_id)
            if not rb or rb.user_id != current_user.id:
                raise HTTPException(404, "Reimbursement not found")

            req = session.exec(
                select(Request).where(Request.reimbursement_id == reimbursement_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
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


class AllTransferRequestResource(Resource):
    """
    Employee Transfer Request Management (List/Create) - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Manages department transfer request lifecycle. Allows employees to track transfer requests
    and submit new ones. Enables efficient department change requests with request tracking.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all transfer requests submitted by the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Returns all transfer requests (pending and completed) with department details and
        current status.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying

        Returns:
            dict: Collection of transfer requests
                - transfers (list[dict]): Array of transfer requests, each containing:
                    - request_id (int): Unique request identifier
                    - transfer_id (int): Transfer record identifier
                    - current_department (str): Current department name
                    - request_department (str): Requested department name
                    - reason (str, optional): Reason for transfer
                    - status (str): "pending" or "completed"

        Error Codes:
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(500): If database query fails
        """
        try:
            q = (
                select(Transfer, Request)
                .join(Request, Request.transfer_id == Transfer.id)
                .where(Transfer.user_id == current_user.id)
            )
            rows = session.exec(q).all()

            data = [
                {
                    "request_id": req.id,
                    "transfer_id": tr.id,
                    "current_department": tr.current_department,
                    "request_department": tr.request_department,
                    "reason": tr.reason,
                    "status": req.status.value,
                }
                for tr, req in rows
            ]

            return {"transfers": data}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def post(
        self,
        payload: TransferCreate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Submit a new department transfer request.

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Creates a transfer request with "pending" status. The request is tracked in the system
        and available for management/HR review.

        Args:
            payload (TransferCreate): Request payload containing:
                - current_department (str, required): Current department name
                - request_department (str, required): Requested department name
                - reason (str, optional): Reason for transfer request
            current_user (User): Authenticated employee user object
            session: Database session for persisting request

        Returns:
            dict: Confirmation message
                - message (str): "Transfer request submitted"

        Error Codes:
            - 400 Bad Request: Missing required fields
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database insertion or commit failures

        Raises:
            HTTPException(500): If transfer creation fails
        """
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
                status=RequestStatusTypeEnum.PENDING,
                user_id=current_user.id,
                transfer_id=tr.id,
            )
            session.add(req)
            session.commit()

            return {
                "message": "Transfer request submitted",
                "request_id": req.id,
                "transfer_id": tr.id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class TransferRequestResource(Resource):
    """
    Individual Transfer Request Operations - Story Point:
    "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

    Handles retrieval, update, and deletion of individual transfer requests. Employees can
    only modify "pending" transfer requests before approval.
    """

    def get(
        self,
        transfer_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific transfer request.

        Args:
            transfer_id (int): The ID of the transfer request to retrieve
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Transfer request details
                - request_id (int): Unique request identifier
                - transfer_id (int): Transfer record identifier
                - current_department (str): Current department
                - request_department (str): Requested department
                - reason (str, optional): Reason for transfer
                - status (str): "pending" or "completed"

        Error Codes:
            - 404 Not Found: Transfer request does not exist or belongs to another employee
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database query failures
        """
        try:
            tr = session.get(Transfer, transfer_id)
            if not tr or tr.user_id != current_user.id:
                raise HTTPException(404, "Transfer request not found")

            req = session.exec(
                select(Request).where(Request.transfer_id == transfer_id)
            ).first()

            return {
                "request_id": req.id,
                "transfer_id": tr.id,
                "current_department": tr.current_department,
                "request_department": tr.request_department,
                "reason": tr.reason,
                "status": req.status.value,
            }

        except HTTPException:
            raise
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
        """
        Update a transfer request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to modify transfer request details before approval. Once approved,
        requests are locked from modification.

        Args:
            transfer_id (int): The ID of the transfer request to update
            payload (TransferCreate): Updated request payload with:
                - current_department (str): Updated current department
                - request_department (str): Updated requested department
                - reason (str, optional): Updated reason
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Transfer request updated"

        Error Codes:
            - 404 Not Found: Transfer request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending"
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If transfer not found
            HTTPException(500): If database commit fails
        """
        try:
            tr = session.get(Transfer, transfer_id)
            if not tr or tr.user_id != current_user.id:
                raise HTTPException(404, "Transfer request not found")

            req = session.exec(
                select(Request).where(Request.transfer_id == transfer_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
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
        """
        Delete a transfer request (only if status is PENDING).

        Story Points Supported:
        - "As an Employee, I want to submit leave and reimbursement requests via forms so that I can track my requests efficiently."

        Allows employees to withdraw pending transfer requests. Once approved, requests
        cannot be deleted.

        Args:
            transfer_id (int): The ID of the transfer request to delete
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Transfer request deleted"

        Error Codes:
            - 404 Not Found: Transfer request does not exist or belongs to another employee
            - 400 Bad Request: Request status is not "pending"
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database deletion failures

        Raises:
            HTTPException(400): If request status is not pending
            HTTPException(404): If transfer not found
            HTTPException(500): If database commit fails
        """
        try:
            tr = session.get(Transfer, transfer_id)
            if not tr or tr.user_id != current_user.id:
                raise HTTPException(404, "Transfer request not found")

            req = session.exec(
                select(Request).where(Request.transfer_id == transfer_id)
            ).first()

            if req.status != RequestStatusTypeEnum.PENDING:
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


class AllHRRequestResource(Resource):
    """
    HR Request Management (List/View All Requests) — Story Point:
    "As an HR Manager, I want to review, track, and manage employee requests so that I can
    efficiently approve or reject leave, reimbursement, and transfer workflows."

    This resource provides HR the ability to view **all employee requests across all departments**,
    including leave requests, reimbursement submissions, and transfer requests. HR can filter
    results based on request type and status, allowing them to quickly focus on pending items
    that require attention.

    HR visibility ensures consistent approval workflows, strengthens compliance, and provides
    centralized monitoring of employee needs without relying on decentralized departmental processes.
    """

    def get(
        self,
        request_type: Optional[str] = None,
        status: Optional[str] = None,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all employee requests with optional filtering.

        Story Points Supported:
        - "As an HR Manager, I want to review pending and completed requests to ensure workflow transparency."
        - "As an HR Manager, I want to filter requests by type or status so that I can
           focus on items requiring urgent action."

        Retrieves **all request types** (leave, reimbursement, transfer) submitted by employees.
        HR can apply optional filters to restrict results based on:
        - request type: "leave", "reimbursement", "transfer"
        - status: "pending", "accepted", "rejected"

        Args:
            request_type (str, optional): Filter by request type. Must be one of:
                - "leave"
                - "reimbursement"
                - "transfer"
            status (str, optional): Filter by request status. Must be one of:
                - "pending"
                - "accepted"
                - "rejected"
            current_user (User): Authenticated HR user object
            session (Session): Active database session for querying

        Returns:
            dict: Collection of employee requests with their linked details.
                - requests (list[dict]): Array of request objects containing:
                    - request_id (int): Unique ID of the request
                    - user_id (int): Employee who submitted the request
                    - request_type (str): "leave", "reimbursement", or "transfer"
                    - status (str): Current status ("pending", "accepted", "rejected")
                    - created_date (datetime): Timestamp of the request submission
                    - details (dict): Additional request-type-specific data

        Error Codes:
            - 401 Unauthorized: User is not HR
            - 400 Bad Request: Invalid request_type or status filter
            - 500 Internal Server Error: Database query failures

        Raises:
            HTTPException(400): If filtering values are invalid
            HTTPException(500): For unexpected database failures
        """

        try:
            if (
                request_type
                and request_type not in RequestTypeEnum.__members__.values()
            ):
                raise HTTPException(400, "Invalid request type")

            if status and status not in RequestStatusTypeEnum.__members__.values():
                raise HTTPException(400, "Invalid status")

            q = select(Request)

            if request_type:
                q = q.where(Request.request_type == request_type)

            if status:
                q = q.where(Request.status == status)

            q = q.order_by(Request.created_date.desc())
            results = session.exec(q).all()

            data = []
            for req in results:
                item = {
                    "request_id": req.id,
                    "user_id": req.user_id,
                    "request_type": req.request_type.value,
                    "status": req.status.value,
                    "created_date": req.created_date,
                }

                if req.leave_id:
                    leave = session.get(Leave, req.leave_id)
                    item["details"] = {
                        "leave_type": leave.leave_type,
                        "from_date": leave.from_date,
                        "to_date": leave.to_date,
                        "reason": leave.reason,
                    }

                elif req.reimbursement_id:
                    rb = session.get(Reimbursement, req.reimbursement_id)
                    item["details"] = {
                        "expense_type": rb.expense_type,
                        "amount": rb.amount,
                        "date_expense": rb.date_expense,
                        "remark": rb.remark,
                    }

                elif req.transfer_id:
                    tr = session.get(Transfer, req.transfer_id)
                    item["details"] = {
                        "current_department": tr.current_department,
                        "request_department": tr.request_department,
                        "reason": tr.reason,
                    }

                data.append(item)

            return {"requests": data}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")


class HRRequestResource(Resource):
    """
    HR Individual Request Management (Accept/Reject) — Story Point:
    "As an HR Manager, I want to approve or reject employee requests so that I can maintain
    proper workflow compliance and ensure timely handling of employee matters."

    This resource enables HR to:
    - View individual request details
    - Accept a pending request
    - Reject a pending request

    HR actions directly update workflow status, helping employees track outcomes and strengthening
    operational efficiency across leave, reimbursement, and transfer workflows.
    """

    def get(
        self,
        request_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific employee request.

        Args:
            request_id (int): ID of the request to retrieve
            current_user (User): Authenticated HR user
            session (Session): Active database session

        Returns:
            dict: Detailed request object with:
                - request_id
                - user_id
                - request_type
                - status
                - created_date
                - details (specific to leave, reimbursement, or transfer)

        Error Codes:
            - 404 Not Found: Request doesn't exist
            - 401 Unauthorized: User is not HR
            - 500 Internal Server Error: Database query issues
        """
        try:
            req = session.get(Request, request_id)
            if not req:
                raise HTTPException(404, "Request not found")

            data = {
                "request_id": req.id,
                "user_id": req.user_id,
                "request_type": req.request_type.value,
                "status": req.status.value,
                "created_date": req.created_date,
            }

            if req.leave_id:
                leave = session.get(Leave, req.leave_id)
                data["details"] = {
                    "leave_type": leave.leave_type,
                    "from_date": leave.from_date,
                    "to_date": leave.to_date,
                    "reason": leave.reason,
                }

            elif req.reimbursement_id:
                rb = session.get(Reimbursement, req.reimbursement_id)
                data["details"] = {
                    "expense_type": rb.expense_type,
                    "amount": rb.amount,
                    "date_expense": rb.date_expense,
                    "remark": rb.remark,
                }

            elif req.transfer_id:
                tr = session.get(Transfer, req.transfer_id)
                data["details"] = {
                    "current_department": tr.current_department,
                    "request_department": tr.request_department,
                    "reason": tr.reason,
                }

            return data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        request_id: int,
        payload: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Update a request's status — accept or reject.

        Story Points Supported:
        - "As an HR Manager, I want to approve or reject employee requests so that I can ensure
        timely decision-making and maintain clear workflow traceability."
        - "As an HR Manager, I want consistent request handling by restricting updates to only
        pending items, preventing accidental modifications after resolution."

        This endpoint allows HR managers to update a request’s workflow status. Only
        **pending** requests are eligible for update, ensuring auditability and preventing
        invalid workflow transitions. HR must explicitly provide the action in the request
        body, ensuring clarity and intentionality during approval or rejection.

        Expected Request Body:
            {
                "action": "accept" | "reject"
            }

        Args:
            request_id (int): Unique ID of the request to update
            payload (dict): JSON body containing the update command, specifically:
                - action (str): Must be one of {"accept", "reject"}
            current_user (User): Authenticated HR user
            session (Session): Active database session

        Returns:
            dict: A message confirming that the request was accepted or rejected.

        Error Codes:
            - 400 Bad Request:
                - Missing "action"
                - Invalid action (not "accept" or "reject")
                - Request is not pending
            - 404 Not Found: Request does not exist
            - 401 Unauthorized: User is not HR
            - 500 Internal Server Error: Database update failures

        Raises:
            HTTPException(400): Invalid or missing update action
            HTTPException(404): If request does not exist
            HTTPException(500): Unexpected server errors
        """
        try:
            req = session.get(Request, request_id)
            if not req:
                raise HTTPException(404, "Request not found")

            if req.status != RequestStatusTypeEnum.PENDING:
                raise HTTPException(400, "Only pending requests can be updated")

            action = payload.get("action")
            if not action:
                raise HTTPException(400, "Missing required field: 'action'")

            if action not in {"accept", "reject"}:
                raise HTTPException(400, "Invalid action. Must be 'accept' or 'reject'")

            if action == "accept":
                req.status = RequestStatusTypeEnum.ACCEPTED
            else:
                req.status = RequestStatusTypeEnum.REJECTED

            session.commit()

            return {"message": f"Request {action}ed successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise HTTPException(500, "Internal server error")
