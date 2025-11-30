#backend/app/api/resources/hr/hr_policy_resource.py
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
    Story Point: Centralized HR Policy Repository Management

    Endpoints:
    - GET  /hr/policies
    - POST /hr/policy/create

    Description:
    Manages the centralized HR policy repository enabling employees to access
    information consistently and HR managers to maintain policies efficiently.
    GenAI enhancement allows intelligent policy recommendations, versioning tracking,
    and automated policy relevance suggestions for different employee roles.

    Authorization:
    - GET: Requires Employee role (all employees can view policies)
    - POST: Requires HR role (only HR can create policies)

    Returns:
    - 200 OK: Policy list or creation confirmation
    - 401 Unauthorized: User not authenticated
    - 403 Forbidden: Insufficient permissions
    """

    def get(
        self,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all HR policies from the centralized repository.

        Purpose:
        Provides employees consistent access to up-to-date HR policies, ensuring
        all staff members have uniform access to policy information. Supports the
        GenAI-enhanced repository by providing searchable, well-organized policies.

        Args:
            current_user: Authenticated user making the request
            _: Authorization check ensuring Employee role
            session: Database session for query execution

        Returns:
            dict: {"policies": [policy_dict, ...]}
            Each policy includes: id, title, content, created_at

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (Employee role required)
            - 500: Database query error
        """
        policies = get_policies(session)
        return {"policies": [p.dict() for p in policies]}

    def post(
        self,
        data: dict,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new HR policy in the centralized repository.

        Purpose:
        Allows HR managers to add new policies to the repository. GenAI can
        analyze policy content for clarity, consistency with existing policies,
        and suggest optimal distribution to relevant employee groups.

        Args:
            data: Dictionary containing policy fields:
                - title (str, required): Policy name/title
                - content (str, required): Full policy text/description
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Expected Payload:
            {
                "title": "Remote Work Policy",
                "content": "Employees may work remotely up to 2 days per week..."
            }

        Returns:
            dict: {"message": "Policy created", "policy": policy_dict}
            Created policy includes: id, title, content, created_at

        Error Codes:
            - 400: Missing required fields (title, content)
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 500: Database creation error
        """
        policy = create_policy(data, session)
        return {"message": "Policy created", "policy": policy.dict()}


class HRPolicyDetailResource(Resource):
    """
    Story Point: Centralized HR Policy Repository Management

    Endpoints:
    - GET /hr/policy/{policy_id}
    - PUT /hr/policy/{policy_id}
    - DELETE /hr/policy/{policy_id}

    Description:
    Provides detailed operations on individual policies within the centralized
    repository. Enables viewing, updating, and deleting specific policies.
    GenAI can track policy changes, suggest improvements, and notify affected
    employees of policy updates.

    Authorization:
    - GET: Requires Employee role (view policies)
    - PUT: Requires HR role (modify policies)
    - DELETE: Requires HR role (remove policies)
    """

    def get(
        self,
        policy_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve a specific HR policy by ID.

        Purpose:
        Fetches detailed information for a single policy, enabling employees
        to read complete policy documents and HR managers to verify policy
        content before distribution or updates.

        Args:
            policy_id: ID of the policy to retrieve
            current_user: Authenticated user making the request
            _: Authorization check ensuring Employee role
            session: Database session for query execution

        Returns:
            dict: {"policy": policy_dict}
            Policy includes: id, title, content, created_at

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (Employee role required)
            - 404: Policy with policy_id not found
            - 500: Database query error
        """
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
        """
        Update an existing HR policy.

        Purpose:
        Allows HR managers to modify policy content and titles to keep the
        centralized repository current. GenAI can highlight changes from
        previous versions and recommend which employee groups should be
        notified of policy updates.

        Args:
            policy_id: ID of the policy to update
            data: Dictionary containing fields to update:
                - title (str, optional): Updated policy name
                - content (str, optional): Updated policy text
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Expected Payload (partial update allowed):
            {
                "title": "Updated Remote Work Policy",
                "content": "Employees may work remotely up to 3 days per week..."
            }

        Returns:
            dict: {"message": "Policy updated", "policy": policy_dict}
            Updated policy includes: id, title, content, created_at

        Error Codes:
            - 400: Invalid or empty payload
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 404: Policy with policy_id not found
            - 500: Database update error
        """
        policy = update_policy(policy_id, data, session)
        return {"message": "Policy updated", "policy": policy.dict()}

    def delete(
        self,
        policy_id: int,
        current_user: User = Depends(get_current_active_user),
        _: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a policy from the centralized repository.

        Purpose:
        Enables HR managers to remove outdated or obsolete policies from the
        repository. Only HR users can perform this action to maintain data
        integrity and audit compliance. GenAI can suggest policies for archival
        based on usage and relevance metrics.

        Args:
            policy_id: ID of the policy to delete
            current_user: Authenticated user making the request
            _: Authorization check ensuring HR role
            session: Database session for query execution

        Returns:
            dict: {"message": "Policy deleted"}

        Error Codes:
            - 401: Authentication failed
            - 403: Insufficient permissions (HR role required)
            - 404: Policy with policy_id not found
            - 500: Database deletion error
        """
        return delete_policy(policy_id, session)
