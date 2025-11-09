from app.api.database.models import Employee
from app.api.database.connection import db_session

def get_all_employees():
    return db_session.query(Employee).all()

def get_employee(emp_id):
    return db_session.query(Employee).filter(Employee.id == emp_id).first()

def create_employee(data):
    new_emp = Employee(
        name=data.name, email=data.email, 
        department=data.department, salary=data.salary
    )
    db_session.add(new_emp)
    db_session.commit()
    return {"message": "Employee created", "id": new_emp.id}

def update_employee(emp_id, data):
    emp = get_employee(emp_id)
    if not emp:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(emp, field, value)
    db_session.commit()
    return {"message": "Employee updated"}

def delete_employee(emp_id):
    emp = get_employee(emp_id)
    if not emp:
        return None
    db_session.delete(emp)
    db_session.commit()
    return {"message": "Employee deleted"}
