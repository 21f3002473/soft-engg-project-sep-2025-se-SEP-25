from .account import AccountResource
from .assistant import AIAssistantResource
from .dashboard import DashboardResource
from .hr_faq import HRFAQCreateResource, HRFAQDetailResource, HRFAQListEmployeeResource
from .learning import LearningResource
from .request import (
    AllLeaveRequestResource,
    AllReimbursementRequestResource,
    AllTransferRequestResource,
    LeaveRequestResource,
    ReimbursementRequestResource,
    TransferRequestResource,
)
from .writing import AllQuickNotesResource, QuickNotesResource

__all__ = [
    "DashboardResource",
    "LearningResource",
    "LeaveRequestResource",
    "ReimbursementRequestResource",
    "TransferRequestResource",
    "AllLeaveRequestResource",
    "AllReimbursementRequestResource",
    "AllTransferRequestResource",
    "HRFAQDetailResource",
    "HRFAQCreateResource",
    "HRFAQListEmployeeResource",
    "QuickNotesResource",
    "AllQuickNotesResource",
    "AccountResource",
    "AIAssistantResource",
]
