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
