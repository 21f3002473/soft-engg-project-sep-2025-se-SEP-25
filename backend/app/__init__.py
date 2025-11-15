import os
from contextlib import asynccontextmanager
from datetime import datetime

from app.api import API
from app.database import create_root_user, get_session, init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_root_user()
    yield


def make_app():
    app = FastAPI(title="se_server", openapi_url="/openapi.json", lifespan=lifespan)

    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    if not allowed_origins or allowed_origins == [""]:

        allowed_origins = ["http://localhost:8080"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
        max_age=600,
    )

    api = API(app)

    # General
    from app.api.resources import UserLoginResource

    api.register_router(UserLoginResource, "/api/login")

    # Employee
    from app.api.resources.employee import (
        AccountResource,
        AIAssistantResource,
        AllLeaveRequestResource,
        AllQuickNotesResource,
        AllReimbursementRequestResource,
        AllToDoResource,
        AllTransferRequestResource,
        AnnouncementAdminDetailResource,
        AnnouncementAdminListCreateResource,
        AnnouncementEmployeeResource,
        CourseAdminDetailResource,
        CourseAdminListCreateResource,
        CourseAssignmentDetailResource,
        CourseAssignmentEmployeeResource,
        CourseAssignmentListResource,
        CourseRecommendationResource,
        DashboardResource,
        HRFAQCreateResource,
        HRFAQDetailResource,
        HRFAQListEmployeeResource,
        LearningResource,
        LeaveRequestResource,
        QuickNotesResource,
        ReimbursementRequestResource,
        ToDoResource,
        TransferRequestResource,
    )

    emp_base_url = "/api/employee"
    hr_base_url = "/api/hr"

    api.register_router(DashboardResource, f"{emp_base_url}/dashboard")
    api.register_router(AllToDoResource, f"{emp_base_url}/todo")
    api.register_router(ToDoResource, f"{emp_base_url}/todo/{{task_id}}")
    api.register_router(AnnouncementEmployeeResource, f"{emp_base_url}/annoucements")
    api.register_router(
        AnnouncementAdminListCreateResource, f"{hr_base_url}/annoucement"
    )
    api.register_router(
        AnnouncementAdminDetailResource, f"{hr_base_url}/annoucement/{{ann_id}}"
    )

    api.register_router(LearningResource, f"{emp_base_url}/learning")
    api.register_router(CourseAssignmentEmployeeResource, f"{emp_base_url}/courses")
    api.register_router(CourseRecommendationResource, f"{emp_base_url}/recommendations")
    api.register_router(CourseAdminListCreateResource, f"{hr_base_url}/course")
    api.register_router(
        CourseAdminDetailResource, f"{hr_base_url}/course/{{course_id}}"
    )
    api.register_router(
        CourseAssignmentListResource, f"{hr_base_url}/course/assign/{{user_id}}"
    )
    api.register_router(
        CourseAssignmentDetailResource,
        f"{hr_base_url}/course/assign/edit/{{assign_id}}",
    )

    api.register_router(AllLeaveRequestResource, f"{emp_base_url}/requests/leave")
    api.register_router(
        AllReimbursementRequestResource, f"{emp_base_url}/requests/reimbursement"
    )
    api.register_router(AllTransferRequestResource, f"{emp_base_url}/requests/transfer")
    api.register_router(
        LeaveRequestResource, f"{emp_base_url}/requests/leave/{{leave_id}}"
    )
    api.register_router(
        ReimbursementRequestResource,
        f"{emp_base_url}/requests/reimbursement/{{reimbursement_id}}",
    )
    api.register_router(
        TransferRequestResource, f"{emp_base_url}/requests/transfer/{{transfer_id}}"
    )

    api.register_router(HRFAQListEmployeeResource, f"{emp_base_url}/hr-faqs")
    api.register_router(HRFAQCreateResource, f"{hr_base_url}/faq")
    api.register_router(HRFAQDetailResource, f"{hr_base_url}/faq/{{faq_id}}")

    api.register_router(AllQuickNotesResource, f"{emp_base_url}/writing")
    api.register_router(QuickNotesResource, f"{emp_base_url}/writing/{{note_id}}")

    api.register_router(AccountResource, f"{emp_base_url}/account")

    api.register_router(AIAssistantResource, f"{emp_base_url}/assistant")

    @app.get("/api")
    def index():
        return {
            "message": "app_running",
            "code": 200,
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S",
            ),
        }

    return app
