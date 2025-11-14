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

    api.register_router(UserLoginResource, "/api/user")

    # Employee
    from app.api.resources.employee import (
        AccountResource,
        AIAssistantResource,
        DashboardResource,
        HRFAQResource,
        LearningResource,
        LeaveRequestResource,
        QuickNotesResource,
        ReimbursementRequestResource,
        TransferRequestResource,
    )

    api.register_router(DashboardResource, "/api/employee/dashboard")
    api.register_router(LearningResource, "/api/employee/learning")

    api.register_router(LeaveRequestResource, "/api/employee/requests/leave")
    api.register_router(
        ReimbursementRequestResource, "/api/employee/requests/reimbursement"
    )
    api.register_router(TransferRequestResource, "/requests/transfer")

    api.register_router(HRFAQResource, "/api/employee/hr-faqs")

    api.register_router(QuickNotesResource, "/api/employee/quick-notes")

    api.register_router(AccountResource, "/api/employee/account")

    api.register_router(AIAssistantResource, "/api/employee/assistant")

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
