# app/api/resources/hr/hr_policy_resource.py
from app.controllers import get_current_active_user
from app.controllers.hr.hr_policy_controller import (
    create_policy,
    delete_policy,
    get_policies,
    get_policy,
    update_policy,
)
from app.database import User, get_session
from app.middleware import require_employee, require_hr
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session


class HRPolicyCollectionResource(Resource):
    """
    GET  /hr/policies
    POST /hr/policy/create
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        policies = get_policies(session)
        return {"policies": [p.dict() for p in policies]}

    def post(
        self,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        policy = create_policy(data, session)
        return {"message": "Policy created", "policy": policy.dict()}


class HRPolicyDetailResource(Resource):
    """
    GET /hr/policy/{policy_id}
    PUT /hr/policy/{policy_id}
    DELETE /hr/policy/{policy_id}
    """

    def get(
        self,
        policy_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        policy = get_policy(policy_id, session)
        return {"policy": policy.dict()}

    def put(
        self,
        policy_id: int,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        policy = update_policy(policy_id, data, session)
        return {"message": "Policy updated", "policy": policy.dict()}

    def delete(
        self,
        policy_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        return delete_policy(policy_id, session)
