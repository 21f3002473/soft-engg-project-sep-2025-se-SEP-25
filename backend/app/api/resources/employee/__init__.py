from .dashboard import DashboardResource
from .learning import LearningResource

from .request import LeaveRequestResource
from .request import ReimbursementRequestResource
from .request import TransferRequestResource
from .request import AllLeaveRequestResource
from .request import AllReimbursementRequestResource
from .request import AllTransferRequestResource

from .hr_faq import HRFAQCreateResource
from .hr_faq import HRFAQDetailResource
from .hr_faq import HRFAQListEmployeeResource

from .writing import QuickNotesResource
from .writing import AllQuickNotesResource

from .account import AccountResource
from .assistant import AIAssistantResource

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
