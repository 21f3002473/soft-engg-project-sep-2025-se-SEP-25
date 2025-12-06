from datetime import timedelta

from app.api.resources import ProtectedResource, UserLoginResource
from app.api.resources.admin_resources.admin_resources import *
from app.api.resources.employee import *

from app.api.resources.hr.hr_assistant_resource import (
    AIAssistantResource as HRAssistantResource,
)

from app.api.resources.hr.hr_chatbot_resource import HRChatbotResource




from app.api.resources.hr.hr_employee_resource import (
    EmployeeDetailResource,
    EmployeeListResource,
)
from app.api.resources.hr.hr_policy_resource import (
    HRPolicyCollectionResource,
    HRPolicyDetailResource,
)
from app.api.resources.hr.hr_project_resource import HRProjectListResource
from app.api.resources.hr.hr_review_resource import (
    HRReviewDetailResource,
    HRReviewsByUserResource,
    HRReviewsListResource,
)
from app.api.resources.pm_resources.clients import (
    ClientRequirementResource,
    ClientsResource,
    ClientUpdatesResource,
)
from app.api.resources.pm_resources.dashboard import PRDashboardResource
from app.api.resources.pm_resources.employee import (
    EmployeePerformanceResource,
    EmployeesResource,
)
from app.api.resources.pm_resources.project import ProjectsResource
from app.controllers import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    Token,
    authenticate_user,
    create_access_token,
)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_restful import Api, Resource


class API:
    def __init__(self, FastAPI: FastAPI):
        super().__init__()
        self.api = Api(FastAPI)

        # General
        self.register_router(UserLoginResource, "/user/login")
        self.register_router(ProtectedResource, "/me")

        # HR
        hr_base_url = "/api/hr"
        self.register_router(HRReviewsListResource, f"{hr_base_url}/reviews")
        self.register_router(HRReviewsListResource, f"{hr_base_url}/review/create")
        self.register_router(
            HRReviewsByUserResource, f"{hr_base_url}/reviews/{{user_id}}"
        )
        self.register_router(
            HRReviewDetailResource, f"{hr_base_url}/review/{{review_id}}"
        )
        self.register_router(HRPolicyCollectionResource, f"{hr_base_url}/policies")
        self.register_router(
            HRPolicyDetailResource, f"{hr_base_url}/policy/{{policy_id}}"
        )
        self.register_router(HRPolicyCollectionResource, f"{hr_base_url}/policy/create")

        self.register_router(EmployeeListResource, f"{hr_base_url}/employees")
        self.register_router(
            EmployeeDetailResource, f"{hr_base_url}/employee/{{emp_id}}"
        )
        self.register_router(HRProjectListResource, f"{hr_base_url}/projects-overview")

        self.register_router(HRAssistantResource, f"{hr_base_url}/assistant")

        self.register_router(HRChatbotResource, f"{hr_base_url}/chatbot")

        # Admin
        admin_base_url = "/api/admin"

        self.register_router(AdminRegistrationResource, f"{admin_base_url}/register")
        self.register_router(AdminDashboardResource, f"{admin_base_url}/summary")
        self.register_router(AdminEmployeeResource, f"{admin_base_url}/employees")
        self.register_router(AdminBackupResource, f"{admin_base_url}/backup-config")
        self.register_router(AdminUpdatesResource, f"{admin_base_url}/updates")
        self.register_router(AdminAccountResource, f"{admin_base_url}/account")
        self.register_router(
            AdminDeleteUserResource, f"{admin_base_url}/deleteusers/{{user_id}}"
        )

        # Product Manager
        pm_base_url = "/api/pm"
        self.register_router(PRDashboardResource, f"{pm_base_url}/dashboard")
        self.register_router(ClientsResource, f"{pm_base_url}/clients")

        self.register_router(
            ClientRequirementResource,
            f"{pm_base_url}/client/requirements/{{client_id}}",
        )
        self.register_router(
            ClientUpdatesResource, f"{pm_base_url}/client/updates/{{client_id}}"
        )
        self.register_router(EmployeesResource, f"{pm_base_url}/employees")
        self.register_router(
            EmployeePerformanceResource,
            f"{pm_base_url}/employee/performance/{{employee_id}}",
        )
        self.register_router(ProjectsResource, f"{pm_base_url}/projects")

        # Employee
        emp_base_url = "/api/employee"
        hr_base_url = "/api/hr"

        self.register_router(DashboardResource, f"{emp_base_url}/dashboard")
        self.register_router(AllToDoResource, f"{emp_base_url}/todo")
        self.register_router(ToDoResource, f"{emp_base_url}/todo/{{task_id}}")
        self.register_router(
            AnnouncementEmployeeResource, f"{emp_base_url}/annoucements"
        )
        self.register_router(
            AnnouncementAdminListResource, f"{hr_base_url}/annoucements"
        )
        self.register_router(
            AnnouncementAdminListCreateResource,
            f"{hr_base_url}/annoucement",
        )
        self.register_router(
            AnnouncementAdminDetailResource,
            f"{hr_base_url}/annoucement/edit/{{ann_id}}",
        )

        self.register_router(
            CourseAssignmentEmployeeResource, f"{emp_base_url}/courses"
        )
        self.register_router(
            EmployeeCourseUpdateByCourseIdResource,
            f"{emp_base_url}/course/{{course_id}}",
        )
        self.register_router(
            CourseRecommendationResource, f"{emp_base_url}/recommendations"
        )
        self.register_router(CourseAdminListCreateResource, f"{hr_base_url}/course")
        self.register_router(
            CourseAdminDetailResource, f"{hr_base_url}/course/{{course_id}}"
        )
        self.register_router(
            CourseAssignmentListResource, f"{hr_base_url}/course/assign/{{user_id}}"
        )
        self.register_router(
            CourseAssignmentDetailResource,
            f"{hr_base_url}/course/assign/edit/{{assign_id}}",
        )

        self.register_router(AllLeaveRequestResource, f"{emp_base_url}/requests/leave")
        self.register_router(
            AllReimbursementRequestResource, f"{emp_base_url}/requests/reimbursement"
        )
        self.register_router(
            AllTransferRequestResource, f"{emp_base_url}/requests/transfer"
        )
        self.register_router(
            LeaveRequestResource, f"{emp_base_url}/requests/leave/{{leave_id}}"
        )
        self.register_router(
            ReimbursementRequestResource,
            f"{emp_base_url}/requests/reimbursement/{{reimbursement_id}}",
        )
        self.register_router(
            TransferRequestResource, f"{emp_base_url}/requests/transfer/{{transfer_id}}"
        )
        self.register_router(AllHRRequestResource, f"{hr_base_url}/request")
        self.register_router(HRRequestResource, f"{hr_base_url}/request/{{request_id}}")

        self.register_router(HRFAQListEmployeeResource, f"{emp_base_url}/hr-faqs")
        self.register_router(HRFAQCreateResource, f"{hr_base_url}/faq")
        self.register_router(HRFAQDetailResource, f"{hr_base_url}/faq/{{faq_id}}")

        self.register_router(AllQuickNotesResource, f"{emp_base_url}/writing")
        self.register_router(QuickNotesResource, f"{emp_base_url}/writing/{{note_id}}")

        self.register_router(AccountResource, f"{emp_base_url}/account")

        self.register_router(AIAssistantResource, f"{emp_base_url}/assistant")
        self.register_router(AIChatHistoryResource, f"{emp_base_url}/assistant/history")

        @FastAPI.post("/token", response_model=Token)
        async def login_for_access_token(
            form_data: OAuth2PasswordRequestForm = Depends(),
        ):
            user = authenticate_user(form_data.email, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}

    def register_router(self, resource: type[Resource], route: str = ""):
        self.api.add_resource(resource(), route)
