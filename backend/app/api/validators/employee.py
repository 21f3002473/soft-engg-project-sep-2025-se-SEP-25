from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeaveCreate(BaseModel):
    leave_type: str
    from_date: datetime
    to_date: datetime
    reason: Optional[str] = None


class ReimbursementCreate(BaseModel):
    expense_type: str
    amount: float
    date_expense: datetime
    remark: Optional[str] = None


class TransferCreate(BaseModel):
    current_department: str
    request_department: str
    reason: Optional[str] = None


class FAQCreate(BaseModel):
    question: str
    answer: str


class FAQOut(BaseModel):
    id: int
    question: str
    answer: str

    model_config = {"from_attributes": True}


class QuickNoteCreate(BaseModel):
    topic: Optional[str] = "Quick Note"
    notes: str


class QuickNoteUpdate(BaseModel):
    topic: Optional[str] = None
    notes: Optional[str] = None


class QuickNoteOut(BaseModel):
    id: int
    topic: str
    notes: str

    model_config = {"from_attributes": True}


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    img_base64: Optional[str] = None
    department_id: Optional[int] = None
    reporting_manager: Optional[int] = None


class AccountOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department_id: Optional[int]
    reporting_manager: Optional[int]
    img_base64: Optional[str]
    department_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
