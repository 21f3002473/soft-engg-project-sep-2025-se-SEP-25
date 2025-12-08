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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

    @app.get("/openapi.yaml", include_in_schema=False)
    def get_openapi_yaml():
        from fastapi.openapi.utils import get_openapi
        from fastapi.responses import Response
        from yaml import dump

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        yaml_schema = dump(openapi_schema, sort_keys=False, default_flow_style=False)
        return Response(
            content=yaml_schema,
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=openapi.yaml"},
        )

    return app


app = make_app()
