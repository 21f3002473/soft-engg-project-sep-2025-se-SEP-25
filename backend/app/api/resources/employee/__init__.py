from .account import AccountResource
from .assistant import AIAssistantResource
from .dashboard import DashboardResource
from .hr_faq import HRFAQResource
from .learning import LearningResource
from .request import (
    LeaveRequestResource,
    ReimbursementRequestResource,
    TransferRequestResource,
)
from .writing import QuickNotesResource

__all__ = [
    "DashboardResource",
    "LearningResource",
    "LeaveRequestResource",
    "ReimbursementRequestResource",
    "TransferRequestResource",
    "HRFAQResource",
    "QuickNotesResource",
    "AccountResource",
    "AIAssistantResource",
]
