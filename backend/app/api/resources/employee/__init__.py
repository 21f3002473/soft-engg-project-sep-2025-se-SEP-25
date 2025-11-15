from .account import AccountResource
from .assistant import AIAssistantResource
from .dashboard import (
    AllToDoResource,
    AnnouncementAdminDetailResource,
    AnnouncementAdminListCreateResource,
    AnnouncementEmployeeResource,
    DashboardResource,
    ToDoResource,
)
from .hr_faq import HRFAQCreateResource, HRFAQDetailResource, HRFAQListEmployeeResource
from .learning import (
    LearningResource,
    CourseAdminDetailResource,
    CourseAdminListCreateResource,
    CourseAssignmentDetailResource,
    CourseAssignmentEmployeeResource,
    CourseAssignmentListResource,
    CourseRecommendationResource,
    EmployeeCourseUpdateByCourseIdResource,
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
    "EmployeeCourseUpdateByCourseIdResource",
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
