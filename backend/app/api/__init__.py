from datetime import timedelta

from app.api.resources import ProtectedResource, UserLoginResource
from app.api.resources.admin_resources.admin_resources import *
from app.api.resources.employee import *
from app.api.resources.pr_resources.clients import (
    ClientRequirementResource,
    ClientsResource,
    ClientUpdatesResource,
)
from app.api.resources.pr_resources.dashboard import PRDashboardResource
from app.api.resources.pr_resources.employee import (
    EmployeePerformanceResource,
    EmployeesResource,
)
from app.api.resources.pr_resources.project import ProjectsResource
from app.controllers import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    Token,
    authenticate_user,
    create_access_token,
)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_restful import Api, Resource

# near other imports in app/api/__init__.py
from app.api.resources.hr.hr_review_resource import (
    HRReviewsListResource,
    HRReviewsByUserResource,
    HRReviewDetailResource,
)
from app.api.resources.hr.hr_policy_resource import (
    HRPolicyCollectionResource,
    HRPolicyDetailResource,
)
from app.api.resources.hr.hr_employee_resource import (
    EmployeeListResource,
    EmployeeDetailResource,
)


class API:
    def __init__(self, FastAPI: FastAPI):
        super().__init__()
        self.api = Api(FastAPI)

        # General
        self.register_router(UserLoginResource, "/user/login")
        self.register_router(ProtectedResource, "/me")
        
        # HR review routes
        self.register_router(HRReviewsListResource, "/hr/reviews")             # GET list, POST create
        self.register_router(HRReviewsByUserResource, "/hr/reviews/{user_id}") # GET reviews by user
        self.register_router(HRReviewDetailResource, "/hr/review/{review_id}") # PUT, DELETE

        # HR policy routes
        self.register_router(HRPolicyCollectionResource, "/hr/policies")       # GET all
        self.register_router(HRPolicyDetailResource, "/hr/policy/{policy_id}") # GET, PUT, DELETE
        self.register_router(HRPolicyCollectionResource, "/hr/policy/create")  # POST create (alternative path)

        # Employee routes
        self.register_router(EmployeeListResource, "/hr/employees")            # GET list
        self.register_router(EmployeeDetailResource, "/hr/employee/{emp_id}")  # GET, PUT, DELETE
        # product manager routes
        self.register_router(PRDashboardResource, "/pr/dashboard")
        self.register_router(ClientsResource, "/pr/clients")

        self.register_router(
            ClientRequirementResource, "/pr/client/requirements/{client_id}"
        )
        self.register_router(ClientUpdatesResource, "/pr/client/updates/{client_id}")
        self.register_router(EmployeesResource, "/pr/employees")
        self.register_router(
            EmployeePerformanceResource, "/pr/employee/performance/{employee_id}"
        )
        self.register_router(ProjectsResource, "/pr/projects")

        # Admin
        admin_base_url = "/api/admin"

        self.register_router(AdminRegistrationResource, f"{admin_base_url}/register")
        self.register_router(AdminDashboardResource, f"{admin_base_url}/summary")
        self.register_router(AdminEmployeeResource, f"{admin_base_url}/employees")
        self.register_router(AdminBackupResource, f"{admin_base_url}/backup-config")
        self.register_router(AdminUpdatesResource, f"{admin_base_url}/updates")
        self.register_router(AdminAccountResource, f"{admin_base_url}n/account")

        # Product Manager
        self.register_router(PRDashboardResource, "/pr/dashboard")

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
            AnnouncementAdminListCreateResource,
            f"{hr_base_url}/annoucement/{{user_id}}",
        )
        self.register_router(
            AnnouncementAdminDetailResource,
            f"{hr_base_url}/annoucement/edit/{{ann_id}}",
        )

        self.register_router(LearningResource, f"{emp_base_url}/learning")
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

        self.register_router(HRFAQListEmployeeResource, f"{emp_base_url}/hr-faqs")
        self.register_router(HRFAQCreateResource, f"{hr_base_url}/faq")
        self.register_router(HRFAQDetailResource, f"{hr_base_url}/faq/{{faq_id}}")

        self.register_router(AllQuickNotesResource, f"{emp_base_url}/writing")
        self.register_router(QuickNotesResource, f"{emp_base_url}/writing/{{note_id}}")

        self.register_router(AccountResource, f"{emp_base_url}/account")

        self.register_router(AIAssistantResource, f"{emp_base_url}/assistant")

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
