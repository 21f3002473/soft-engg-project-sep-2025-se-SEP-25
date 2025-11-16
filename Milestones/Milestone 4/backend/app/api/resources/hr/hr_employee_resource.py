from app.controllers import get_current_active_user
from app.controllers.hr.hr_employee_controller import (
    delete_employee,
    get_employee,
    list_employees,
    update_employee,
)
from app.database import User, get_session
from app.middleware import require_hr, require_pm, require_root
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session


class EmployeeListResource(Resource):
    """
    Story Point: HR Policy Repository Management & Performance Review Scheduling

    Endpoint: GET /hr/employees

    Description:
    Provides HR managers with centralized access to all employees, enabling consistent
    management of HR policies and performance review scheduling. With GenAI enhancement,
    this enables intelligent querying and filtering of employee data for optimized
    review cycles and policy distribution.

    Authorization: Requires HR role

    Returns:
    - 200 OK: List of all employees with their details
    - 401 Unauthorized: User not authenticated
    - 403 Forbidden: User lacks HR role permission
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all employees for HR management and policy/review operations.

        Purpose:
        Lists all active employees to support centralized HR policy repository access
        and performance review scheduling. GenAI can analyze this data to recommend
        optimal review timing and policy relevance for each employee.

        Args:
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Returns:
            dict: {"employees": [employee_dict, ...]}

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 500: Database query error
        """
        employees = list_employees(session)
        return {"employees": [e.dict() for e in employees]}


class EmployeeDetailResource(Resource):
    """
    Story Point: HR Policy Repository Management & Performance Review Scheduling

    Endpoints:
    - GET /hr/employee/{emp_id}
    - PUT /hr/employee/{emp_id}
    - DELETE /hr/employee/{emp_id}

    Description:
    Provides granular control over individual employee records, policies, and
    performance reviews. Supports CRUD operations for maintaining accurate employee
    data, enabling targeted policy application and personalized review scheduling.
    GenAI integration allows intelligent recommendations for policy updates and
    review frequency optimization based on employee history and performance trends.

    Authorization:
    - GET: Requires PM role
    - PUT: Requires HR role
    - DELETE: Requires Root role
    """

    def get(
        self,
        emp_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve detailed information for a specific employee.

        Purpose:
        Fetches complete employee record for policy access verification and
        performance review history retrieval. Enables PMs to review employee
        details necessary for policy compliance and review planning.

        Args:
            emp_id: Employee ID to retrieve
            current_user: Authenticated user making the request
            _: Authorization check ensuring PM role
            session: Database session for query execution

        Returns:
            dict: {"employee": employee_dict}

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (PM role required)
            - 404: Employee with emp_id not found
            - 500: Database query error
        """
        emp = get_employee(emp_id, session)
        return {"employee": emp.dict()}

    def put(
        self,
        emp_id: int,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Update employee information and policy assignments.

        Purpose:
        Modifies employee records to reflect policy changes, role updates, and
        status changes affecting review schedules. GenAI can suggest optimal
        review timing adjustments based on role or policy changes.

        Args:
            emp_id: Employee ID to update
            data: Dictionary containing fields to update (name, email, role, is_active)
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Allowed Fields: name, email, role, is_active

        Returns:
            dict: {"message": "Employee updated", "employee": updated_employee_dict}

        Error Codes:
            - 400: Invalid or disallowed fields in payload
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 404: Employee with emp_id not found
            - 500: Database update error
        """
        emp = update_employee(emp_id, data, session)
        return {"message": "Employee updated", "employee": emp.dict()}

    def delete(
        self,
        emp_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        """
        Delete an employee record from the system.

        Purpose:
        Removes employee records for resigned, terminated, or test accounts.
        Only Root users can perform this action to maintain data integrity
        and audit compliance for HR policies and performance reviews.

        Args:
            emp_id: Employee ID to delete
            current_user: Authenticated user making the request
            _: Authorization check ensuring Root role
            session: Database session for query execution

        Returns:
            dict: {"message": "Employee deleted"}

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (Root role required)
            - 404: Employee with emp_id not found
            - 500: Database deletion error
        """
        return delete_employee(emp_id, session)
