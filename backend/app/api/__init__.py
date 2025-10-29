from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi_restful import Api, Resource
from fastapi.security import OAuth2PasswordRequestForm

from app.api.resources import UserLoginResource, ProtectedResource
from app.controllers import (
    Token,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class API:
    def __init__(self, FastAPI: FastAPI):
        super().__init__()
        self.api = Api(FastAPI)
        self.register_router(UserLoginResource, "/user/login")
        self.register_router(ProtectedResource, "/me")

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
