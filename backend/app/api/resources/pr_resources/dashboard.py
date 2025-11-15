from logging import getLogger

from app.database import User, get_session
from app.database.product_manager_models import Client, Project, StatusTypeEnum
from app.middleware import require_pm
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session, select, func

logger = getLogger(__name__)


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

            # Query clients from database
            statement = select(Client)
            clients = session.exec(statement).all()

            # Format client data
            client_list = [
                {
                    "id": client.id,
                    "clientname": client.client_name,
                    "description": client.detail_base64 or f"Details about {client.client_name}",
                }
                for client in clients
            ]

            # Query projects from database
            project_statement = select(Project)
            projects = session.exec(project_statement).all()

            # Format project data
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

            # Calculate project statistics
            total_projects = len(projects)
            active_projects = sum(1 for p in projects if p.status == StatusTypeEnum.IN_PROGRESS)
            completed_projects = sum(1 for p in projects if p.status == StatusTypeEnum.COMPLETED)
            pending_projects = sum(1 for p in projects if p.status == StatusTypeEnum.PENDING)

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


