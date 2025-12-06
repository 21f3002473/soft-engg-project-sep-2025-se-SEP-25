from .account import AccountResource
from .assistant import AIAssistantResource, AIChatHistoryResource
from .dashboard import (
    AllToDoResource,
    AnnouncementAdminDetailResource,
    AnnouncementAdminListCreateResource,
    AnnouncementAdminListResource,
    AnnouncementEmployeeResource,
    DashboardResource,
    ToDoResource,
)
from .hr_faq import HRFAQCreateResource, HRFAQDetailResource, HRFAQListEmployeeResource
from .learning import (
    CourseAdminDetailResource,
    CourseAdminListCreateResource,
    CourseAssignmentDetailResource,
    CourseAssignmentEmployeeResource,
    CourseAssignmentListResource,
    CourseRecommendationResource,
    EmployeeCourseUpdateByCourseIdResource,
)
from .request import (
    AllHRRequestResource,
    AllLeaveRequestResource,
    AllReimbursementRequestResource,
    AllTransferRequestResource,
    HRRequestResource,
    LeaveRequestResource,
    ReimbursementRequestResource,
    TransferRequestResource,
)
from .writing import AllQuickNotesResource, QuickNotesResource

__all__ = [
    "DashboardResource",
    "AllToDoResource",
    "ToDoResource",
    "AnnouncementAdminListCreateResource",
    "AnnouncementAdminDetailResource",
    "AnnouncementEmployeeResource",
    "AnnouncementAdminListResource",
    "CourseAdminListCreateResource",
    "CourseAdminDetailResource",
    "CourseAssignmentListResource",
    "CourseAssignmentDetailResource",
    "CourseAssignmentEmployeeResource",
    "CourseRecommendationResource",
    "EmployeeCourseUpdateByCourseIdResource",
    "LeaveRequestResource",
    "ReimbursementRequestResource",
    "TransferRequestResource",
    "AllLeaveRequestResource",
    "AllReimbursementRequestResource",
    "AllTransferRequestResource",
    "AllHRRequestResource",
    "HRRequestResource",
    "HRFAQDetailResource",
    "HRFAQCreateResource",
    "HRFAQListEmployeeResource",
    "QuickNotesResource",
    "AllQuickNotesResource",
    "AccountResource",
    "AIAssistantResource",
    "AIChatHistoryResource",
]
