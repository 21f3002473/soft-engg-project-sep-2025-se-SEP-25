from datetime import timedelta

from app.api.resources import ProtectedResource, UserLoginResource
from app.controllers import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    authenticate_user,
    create_access_token,
)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_restful import Api, Resource

from app.api.resources.pr_resources.dashboard import PRDashboardResource
from app.api.resources.pr_resources.clients import ClientsResource, ClientRequirementResource, ClientUpdatesResource
from app.api.resources.pr_resources.employee import EmployeesResource, EmployeePerformanceResource
from app.api.resources.pr_resources.project import ProjectsResource


class API:
    def __init__(self, FastAPI: FastAPI):
        super().__init__()
        self.api = Api(FastAPI)
        self.register_router(UserLoginResource, "/user/login")
        self.register_router(ProtectedResource, "/me")
        # product manager routes
        self.register_router(PRDashboardResource, "/pr/dashboard")
        self.register_router(ClientsResource, "/pr/clients")

        self.register_router(ClientRequirementResource, "/pr/client/requirements/{client_id}")
        self.register_router(ClientUpdatesResource, "/pr/client/updates/{client_id}")
        self.register_router(EmployeesResource, "/pr/employees")
        self.register_router(EmployeePerformanceResource, "/pr/employee/performance/{employee_id}")
        self.register_router(ProjectsResource, "/pr/projects")

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
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}

    def register_router(self, resource: type[Resource], route: str = ""):
        self.api.add_resource(resource(), route)
