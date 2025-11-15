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
        DashboardResource,
        LearningResource,
        LeaveRequestResource,
        ReimbursementRequestResource,
        TransferRequestResource,
        AllLeaveRequestResource,
        AllReimbursementRequestResource,
        AllTransferRequestResource,
        HRFAQCreateResource,
        HRFAQDetailResource,
        HRFAQListEmployeeResource,
        AllQuickNotesResource,
        QuickNotesResource,
        AccountResource,
        AIAssistantResource,
    )

    emp_base_url = "/api/employee"

    api.register_router(DashboardResource, f"{emp_base_url}/dashboard")
    api.register_router(LearningResource, f"{emp_base_url}/learning")

    api.register_router(AllLeaveRequestResource, f"{emp_base_url}/requests/leave")
    api.register_router(
        AllReimbursementRequestResource, f"{emp_base_url}/requests/reimbursement"
    )
    api.register_router(AllTransferRequestResource, f"{emp_base_url}/requests/transfer")
    api.register_router(LeaveRequestResource, f"{emp_base_url}/requests/leave/{{leave_id}}")
    api.register_router(
        ReimbursementRequestResource,
        f"{emp_base_url}/requests/reimbursement/{{reimbursement_id}}",
    )
    api.register_router(TransferRequestResource, f"{emp_base_url}/requests/transfer/{{transfer_id}}")

    api.register_router(HRFAQListEmployeeResource, f"{emp_base_url}/hr-faqs")
    api.register_router(HRFAQCreateResource, "/api/hr/faq")
    api.register_router(HRFAQDetailResource, "/api/hr/faq/{faq_id}")

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
