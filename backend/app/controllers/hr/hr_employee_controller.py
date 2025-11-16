# app/controllers/hr/hr_employee_controller.py
from typing import Any, Dict, List

from app.database import User
from fastapi import HTTPException
from sqlmodel import Session, select


def list_employees(session: Session) -> List[User]:
    return session.exec(select(User).order_by(User.id)).all()


def get_employee(emp_id: int, session: Session) -> User:
    emp = session.get(User, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


def update_employee(emp_id: int, payload: Dict[str, Any], session: Session) -> User:
    emp = session.get(User, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Only update allowed fields (add more if needed)
    allowed = {"name", "email", "role", "is_active"}
    for k, v in payload.items():
        if k in allowed:
            setattr(emp, k, v)

    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


def delete_employee(emp_id: int, session: Session) -> dict:
    emp = session.get(User, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(emp)
    session.commit()
    return {"message": "Employee deleted"}
