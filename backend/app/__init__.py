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

    API(app)

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


app = make_app()
