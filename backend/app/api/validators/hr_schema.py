from pydantic import BaseModel, EmailStr
from typing import Optional

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    salary: float

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    salary: Optional[float] = None
