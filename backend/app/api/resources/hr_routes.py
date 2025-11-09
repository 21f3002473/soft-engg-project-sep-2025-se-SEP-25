from fastapi import APIRouter, HTTPException
from app.api.validators.hr_schema import EmployeeCreate, EmployeeUpdate
from app.api.controllers.hr_controller import (
    get_all_employees,
    get_employee,
    create_employee,
    update_employee,
    delete_employee
)

router = APIRouter()

@router.get("/")
def list_employees():
    return get_all_employees()

@router.get("/{emp_id}")
def get_employee_by_id(emp_id: int):
    employee = get_employee(emp_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/")
def add_employee(data: EmployeeCreate):
    return create_employee(data)

@router.put("/{emp_id}")
def modify_employee(emp_id: int, data: EmployeeUpdate):
    return update_employee(emp_id, data)

@router.delete("/{emp_id}")
def remove_employee(emp_id: int):
    return delete_employee(emp_id)
