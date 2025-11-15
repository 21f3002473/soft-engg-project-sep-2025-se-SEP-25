from .dashboard import (
    AllToDoResource,
    DashboardResource,
    ToDoResource,
    AnnouncementAdminListCreateResource,
    AnnouncementAdminDetailResource,
    AnnouncementEmployeeResource,
)

from .hr_faq import HRFAQCreateResource, HRFAQDetailResource, HRFAQListEmployeeResource

from .learning import (
    LearningResource,
    CourseAdminListCreateResource,
    CourseAdminDetailResource,
    CourseAssignmentListResource,
    CourseAssignmentDetailResource,
    CourseAssignmentEmployeeResource,
    CourseRecommendationResource,
)

from .request import (
    AllLeaveRequestResource,
    AllReimbursementRequestResource,
    AllTransferRequestResource,
    LeaveRequestResource,
    ReimbursementRequestResource,
    TransferRequestResource,
)

from .writing import AllQuickNotesResource, QuickNotesResource

from .account import AccountResource

from .assistant import AIAssistantResource

__all__ = [
    "DashboardResource",
    "AllToDoResource",
    "ToDoResource",
    "AnnouncementAdminListCreateResource",
    "AnnouncementAdminDetailResource",
    "AnnouncementEmployeeResource",
    "LearningResource",
    "CourseAdminListCreateResource",
    "CourseAdminDetailResource",
    "CourseAssignmentListResource",
    "CourseAssignmentDetailResource",
    "CourseAssignmentEmployeeResource",
    "CourseRecommendationResource",
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
