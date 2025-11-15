import os
from contextlib import asynccontextmanager
from datetime import datetime

from app.api import API
from app.database import create_root_user, get_session, init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from backend.app import api


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

    # Admin
    from app.api.resources.admin_resources.admin_resources import (
        AdminRegistrationResource,
        AdminDashboardResource,
        AdminEmployeeResource,
        AdminBackupResource,
        AdminUpdatesResource,
        AdminAccountResource,
    )

    api.register_router(AdminRegistrationResource, "/api/admin/register")
    api.register_router(AdminDashboardResource, "/api/admin/summary")
    api.register_router(AdminEmployeeResource, "/api/admin/employees")
    api.register_router(AdminBackupResource, "/api/admin/backup-config")
    api.register_router(AdminUpdatesResource, "/api/admin/updates")
    api.register_router(AdminAccountResource, "/api/admin/account")

    @app.get("/")
    def index():
        return {
            "message": "app_running",
            "code": 200,
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S",
            ),
        }

    return app


# Create app instance for uvicorn to reference
app = make_app()
