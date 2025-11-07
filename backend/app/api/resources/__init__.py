from datetime import timedelta
from logging import getLogger

from app.api.validators import UserLoginValidator
from app.controllers import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.database import User, get_session
from app.middleware import (
    Role,
    can_manage_employees,
    can_manage_products,
    require_employee,
    require_hr,
    require_pm,
    require_root,
)
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlalchemy import log
from sqlmodel import Session

logger = getLogger(__name__)


class UserLoginResource(Resource):
    def get(self):
        return {"message": "User login endpoint"}

    def post(self, data: UserLoginValidator, session: Session = Depends(get_session)):
        """login_function

        Keyword arguments:
        UserLoginValidator -- {email: str, password: str}

        #
        - email: str -- user's email
        - password: str -- user's password

        ```javascript
        // Example request body
        {
            "email": "user@example.com",
            "password": "securepassword"
        }
        ```
        Return: A message and token upon successful login
        """

        logger.info("user login details" + str(data))
        user = authenticate_user(data.email, data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "message": "User logged in successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
        }


class ProtectedResource(Resource):
    def get(self, current_user: User = Depends(get_current_active_user)):
        """Protected endpoint that requires authentication"""
        return {
            "email": current_user.email,
            "name": current_user.name,
            "id": current_user.id,
            "role": current_user.role,
        }


class AdminResource(Resource):
    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_root()),
    ):
        """ROOT only - System administration endpoint"""
        return {
            "message": "Admin access granted",
            "user": current_user.name,
            "role": current_user.role,
        }


class EmployeeManagementResource(Resource):
    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR or ROOT - View all employees"""

        return {
            "message": "Employee records access",
            "accessed_by": current_user.name,
            "role": current_user.role,
        }

    def post(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(can_manage_employees()),
        session: Session = Depends(get_session),
    ):
        """HR or ROOT - Create/manage employees"""
        return {
            "message": "Employee created",
            "created_by": current_user.name,
        }


class ProductManagementResource(Resource):
    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """PM or ROOT - View products"""
        return {
            "message": "Product list",
            "accessed_by": current_user.name,
            "role": current_user.role,
        }

    def post(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(can_manage_products()),
        session: Session = Depends(get_session),
    ):
        """PM or ROOT - Create/manage products"""
        return {
            "message": "Product created",
            "created_by": current_user.name,
        }


class ProfileResource(Resource):
    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
    ):
        """Any authenticated user - View own profile"""
        return {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
        }

    def put(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Any authenticated user - Update own profile"""

        return {
            "message": "Profile updated",
            "user": current_user.name,
        }
