# app/api/resources/hr/hr_employee_resource.py
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
    GET /hr/employees
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        employees = list_employees(session)
        return {"employees": [e.dict() for e in employees]}


class EmployeeDetailResource(Resource):
    """
    GET /hr/employee/{emp_id}
    PUT /hr/employee/{emp_id}
    DELETE /hr/employee/{emp_id}
    """

    def get(
        self,
        emp_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
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
        emp = update_employee(emp_id, data, session)
        return {"message": "Employee updated", "employee": emp.dict()}

    def delete(
        self,
        emp_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
        session: Session = Depends(get_session),
    ):
        return delete_employee(emp_id, session)
