from logging import getLogger
from typing import Optional

from app.database import User, get_session
from app.database.product_manager_models import Client, Project, StatusTypeEnum
from app.middleware import require_pm
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

logger = getLogger(__name__)


class ClientCreateModel(BaseModel):
    client_id: str
    client_name: str
    email: str
    image_base64: Optional[str] = None


class PRDashboardResource(Resource):
    """
    PRDashboardResource
    ===================

    A resource class for retrieving and displaying project manager dashboard data.

    This resource provides a GET endpoint that aggregates and returns:
    - Current user information
    - List of all clients with their details
    - List of all projects with their metadata
    - Project statistics (total, active, completed, pending)

    Attributes:
        None

    Methods:
        get(current_user: User, session: Session) -> dict:
            Retrieves dashboard data for the logged-in project manager.

            Args:
                current_user (User): The authenticated project manager user (injected via require_pm() dependency).
                session (Session): Database session for executing queries (injected via get_session dependency).

            Returns:
                dict: A dictionary containing:
                    - message (str): Status message
                    - data (dict): Dashboard data including:
                        - user (dict): Current user details (id, name, email, role)
                        - ClientList (list[dict]): List of clients with id, clientname, and description
                        - projects (list[dict]): List of projects with id, project_id, project_name,
                                                description, status, client_id, manager_id
                        - stats (dict): Project statistics with counts of total, active, completed,
                                       and pending projects
                - On error, returns (dict, int): Error message with 500 status code

            Raises:
                None (Exceptions are caught and logged internally)

            Logs:
                - Info: Dashboard access by user email
                - Error: Any exceptions encountered during execution with full traceback
    """

    def get(
        self,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """PM Dashboard - View project manager dashboard data"""
        try:
            logger.info(f"Dashboard accessed by: {current_user.email}")

            statement = select(Client)
            clients = session.exec(statement).all()

            client_list = [
                {
                    "id": client.id,
                    "clientname": client.client_name,
                    "image": client.image_base64,
                }
                for client in clients
            ]

            project_statement = select(Project)
            projects = session.exec(project_statement).all()

            project_list = [
                {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "status": project.status,
                    "client_id": project.client_id,
                    "manager_id": project.manager_id,
                }
                for project in projects
            ]

            total_projects = len(projects)
            active_projects = sum(
                1 for p in projects if p.status == StatusTypeEnum.IN_PROGRESS
            )
            completed_projects = sum(
                1 for p in projects if p.status == StatusTypeEnum.COMPLETED
            )
            pending_projects = sum(
                1 for p in projects if p.status == StatusTypeEnum.PENDING
            )

            return {
                "message": "Dashboard data retrieved successfully",
                "data": {
                    "user": {
                        "id": current_user.id,
                        "name": current_user.name,
                        "email": current_user.email,
                        "role": current_user.role,
                    },
                    "ClientList": client_list,
                    "projects": project_list,
                    "stats": {
                        "total_projects": total_projects,
                        "active_projects": active_projects,
                        "completed_projects": completed_projects,
                        "pending_projects": pending_projects,
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error in dashboard: {str(e)}", exc_info=True)
            return {
                "message": "Internal server error",
                "error": str(e),
                "status": "error",
            }, 500

    def post(
        self,
        client: ClientCreateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """PM Dashboard this is api is to create new clients"""
        try:

            existing = session.exec(
                select(Client).where(Client.client_id == client.client_id)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Client ID already exists")

            new_client = Client(
                client_id=client.client_id,
                client_name=client.client_name,
                email=client.email,
                image_base64=client.image_base64,
            )

            session.add(new_client)
            session.commit()
            session.refresh(new_client)

            return {
                "message": "Client created successfully",
                "data": {
                    "id": new_client.id,
                    "client_id": new_client.client_id,
                    "client_name": new_client.client_name,
                    "email": new_client.email,
                    "image": new_client.image_base64,
                },
            }
        except HTTPException:
            raise
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error creating client: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Database integrity error. Please contact administrator.",
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating client: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
