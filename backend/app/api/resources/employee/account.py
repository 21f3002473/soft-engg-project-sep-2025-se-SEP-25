from logging import getLogger

from app.api.validators import AccountOut, AccountUpdate
from app.database import Department, User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session

logger = getLogger(__name__)


class AccountResource(Resource):
    """
    Employee Account Management Resource - Core Employee Profile Operations

    Manages employee account information and profile updates. Allows employees to view and
    modify their personal information including name, email, profile image, department assignment,
    and reporting manager relationship. This is a foundational resource for employee self-service
    account management across all employee-facing story points.

    Supports employee autonomy in managing their profile data and ensuring accurate HR records
    without requiring HR intervention for routine updates.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve the logged-in employee's account profile information.

        Provides complete profile details including personal information, role, department
        assignment, and reporting structure. Department name is resolved from department_id
        for easier frontend consumption.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying department information

        Returns:
            AccountOut: Serialized employee account information containing:
                - id (int): Unique employee identifier
                - name (str): Employee full name
                - email (str): Employee email address
                - role (str): Employee role (e.g., "employee", "product_manager", "human_resource")
                - department_id (int, optional): Department ID if assigned
                - reporting_manager (int, optional): User ID of reporting manager
                - img_base64 (str, optional): Base64-encoded profile image
                - department_name (str, optional): Human-readable department name

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
            - 500 Internal Server Error: Database query failures or session errors

        Raises:
            HTTPException(500): If department lookup fails or database error occurs
        """
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
        except HTTPException:
            raise
        except Exception:
            logger.error("Account GET error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        payload: AccountUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Update the logged-in employee's account profile information.

        Allows employees to modify their personal profile data. Only fields included in the
        request payload are updated (partial updates supported). Employees can update:
        - Name and email address
        - Profile image (base64-encoded)
        - Department assignment (if available for self-assignment)
        - Reporting manager relationship (if configurable)

        Args:
            payload (AccountUpdate): Request payload with optional fields:
                - name (str, optional): Updated employee name
                - email (str, optional): Updated email address
                - img_base64 (str, optional): Base64-encoded profile image
                - department_id (int, optional): Updated department assignment
                - reporting_manager (int, optional): Updated reporting manager ID
            current_user (User): Authenticated employee user object
            session (Session): Database session for persisting updates

        Returns:
            dict: Confirmation message
                - message (str): "Account updated successfully"

        Error Codes:
            - 400 Bad Request: Invalid field values or constraint violations
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update or commit failures

        Raises:
            HTTPException(500): If database commit fails or update operation fails
        """
        try:
            update_data = payload.model_dump(exclude_unset=True)

            user = session.merge(current_user)

            restricted = {"id", "role", "created_at"}
            if restricted & update_data.keys():
                raise HTTPException(400, "You cannot update these fields")

            for key, value in update_data.items():
                setattr(user, key, value)

            session.commit()
            session.refresh(user)

            return {"message": "Account updated successfully"}

        except HTTPException:
            raise
        except ValueError as ve:
            logger.error(ve, exc_info=True)
            raise HTTPException(400, "Invalid input data")
        except Exception as e:
            logger.error("Account Update error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def delete(
        self,
        current_user: User = Depends(require_employee()),
    ):
        """
        Client-side logout endpoint.

        This is a symbolic endpoint for logout workflow. In practice, logout is handled
        client-side by deleting the authentication token. This endpoint acknowledges the
        logout request and can be used for server-side cleanup or audit logging if needed.

        Args:
            current_user (User): Authenticated employee user object

        Returns:
            dict: Logout confirmation message
                - message (str): "Logged out successfully"

        Note:
            Authentication token deletion is performed on the client side. This endpoint
            serves as a confirmation point and potential hook for server-side logging.
        """
        return {"message": "Logged out successfully"}
