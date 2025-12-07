from logging import getLogger
from typing import Optional

from app.database import User, get_session
from app.database.product_manager_models import (
    Client,
    Project,
    Requirement,
    StatusTypeEnum,
    Update,
)
from app.middleware import require_pm
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from pydantic import BaseModel
from sqlmodel import Session, select

logger = getLogger(__name__)


class ProjectCreateModel(BaseModel):
    project_id: str
    project_name: str
    description: Optional[str] = None
    status: Optional[StatusTypeEnum] = StatusTypeEnum.PENDING
    client_id: int
    manager_id: Optional[int] = None


class ProjectUpdateModel(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusTypeEnum] = None
    manager_id: Optional[int] = None


class ProjectsResource(Resource):
    """
    ProjectsResource handles CRUD operations for projects.

    This resource provides endpoints for managing projects with the following operations:

    Methods:
        get: Retrieve all projects accessible to the current user (requires PM role)
        post: Create a new project with validation of client and manager existence
        put: Update an existing project's details
        delete: Delete a project by its ID

    All operations require PM (Project Manager) authentication and maintain audit logs
    of actions performed by users.
    """

    def get(
        self,
        id_client: Optional[int] = None,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all projects or filter by client ID.

        Fetches a list of projects. If id_client is provided, returns only projects
        for that client. Otherwise, returns all projects.
        Only accessible by users with Project Manager (PM) role.

        Args:
            id_client (int, optional): Client ID to filter projects by.
            current_user (User): The authenticated user making the request, must have PM role.
                Obtained via dependency injection using `require_pm()`.
            session (Session): Database session for executing queries.
                Obtained via dependency injection using `get_session()`.

        Returns:
            dict: A dictionary containing:
                - message (str): Success message indicating projects were retrieved.
                - data (dict): Contains:
                    - projects (list): List of project dictionaries, each containing:
                        - id (str): Unique project identifier
                        - project_id (str): Project ID
                        - project_name (str): Name of the project
                        - description (str): Project description
                        - status (str): Current status of the project
                        - client_id (str): Associated client identifier
                        - manager_id (str): Associated manager identifier
                    - total_projects (int): Total number of projects retrieved

        Raises:
            HTTPException: Status code 500 if an error occurs during project retrieval.

        Logs:
            - Info: Logs the user email when fetching projects begins.
            - Error: Logs any exceptions that occur during the retrieval process.
        """
        try:
            logger.info(f"Fetching projects by {current_user.email}")

            if id_client is not None:
                statement = select(Project).where(Project.client_id == id_client)
            else:
                statement = select(Project)

            projects = session.exec(statement).all()

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

            return {
                "message": "Projects retrieved successfully",
                "data": {
                    "projects": project_list,
                    "total_projects": len(project_list),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def post(
        self,
        data: ProjectCreateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Create a new project.

        This endpoint creates a new project with the provided details. Only Project Managers (PM) are authorized to create projects.

        Args:
            data (ProjectCreateModel): The project creation data containing:
                - project_id (str): Unique identifier for the project
                - project_name (str): Name of the project
                - description (str): Project description
                - status (str): Initial status of the project
                - client_id (int): ID of the associated client
                - manager_id (int, optional): ID of the project manager
            current_user (User): The authenticated user making the request (must be a PM)
            session (Session): Database session for ORM operations

        Returns:
            dict: A dictionary containing:
                - message (str): Success message
                - data (dict): Created project details including id, project_id, project_name, status, and client_id

        Raises:
            HTTPException (400): If project_id already exists
            HTTPException (404): If the specified client or manager is not found
            HTTPException (500): If an unexpected error occurs during project creation

        Notes:
            - Requires PM role authorization
            - Automatically rolls back transaction on error
            - Logs project creation activity and any errors
        """
        try:
            logger.info(f"Creating project by {current_user.email}")

            existing = session.exec(
                select(Project).where(Project.project_id == data.project_id)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Project ID already exists")

            client = session.exec(
                select(Client).where(Client.id == data.client_id)
            ).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            if data.manager_id:
                manager = session.exec(
                    select(User).where(User.id == data.manager_id)
                ).first()
                if not manager:
                    raise HTTPException(status_code=404, detail="Manager not found")

            new_project = Project(
                project_id=data.project_id,
                project_name=data.project_name,
                description=data.description,
                status=data.status,
                client_id=data.client_id,
                manager_id=data.manager_id,
            )
            session.add(new_project)
            session.commit()
            session.refresh(new_project)

            return {
                "message": "Project created successfully",
                "data": {
                    "id": new_project.id,
                    "project_id": new_project.project_id,
                    "project_name": new_project.project_name,
                    "status": new_project.status,
                    "client_id": new_project.client_id,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating project: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        project_id: int,
        data: ProjectUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Update an existing project with the provided details.
        Args:
            project_id (int): The ID of the project to update.
            data (ProjectUpdateModel): The project data to update containing optional fields:
                - project_name (str, optional): New project name
                - description (str, optional): New project description
                - status (str, optional): New project status
                - manager_id (int, optional): New project manager ID
            current_user (User): The currently authenticated user (must be a project manager).
                Injected via Depends(require_pm()).
            session (Session): The database session for executing queries.
                Injected via Depends(get_session).
        Returns:
            dict: A dictionary containing:
                - message (str): Success message indicating the project was updated
                - data (dict): Updated project information including id, project_id,
                  project_name, status, and description
        Raises:
            HTTPException:
                - 404 if project with given project_id is not found
                - 404 if manager_id is provided but the manager user is not found
                - 500 if an internal server error occurs during the update process
        Note:
            Only fields with non-None values in the request data will be updated.
            Changes are committed to the database and the updated project is refreshed.
        """
        try:
            logger.info(f"Updating project {project_id} by {current_user.email}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            if data.project_name is not None:
                project.project_name = data.project_name
            if data.description is not None:
                project.description = data.description
            if data.status is not None:
                project.status = data.status
            if data.manager_id is not None:

                manager = session.exec(
                    select(User).where(User.id == data.manager_id)
                ).first()
                if not manager:
                    raise HTTPException(status_code=404, detail="Manager not found")
                project.manager_id = data.manager_id

            session.add(project)
            session.commit()
            session.refresh(project)

            client = session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            return {
                "message": "Project updated successfully",
                "data": {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "status": project.status,
                    "client": (
                        {
                            "id": client.client_id if client else None,
                            "name": client.client_name if client else None,
                            "email": client.email if client else None,
                        }
                        if client
                        else None
                    ),
                    "manager_id": project.manager_id,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating project: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(
        self,
        project_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a project by its ID.
        This endpoint allows a Project Manager to delete a project from the system.
        The project must exist in the database, otherwise a 404 error is raised.
        Args:
            project_id (int): The unique identifier of the project to be deleted.
            current_user (User): The authenticated user performing the delete operation.
                                Must have Project Manager role (verified by require_pm() dependency).
            session (Session): The database session for executing queries and transactions.
        Returns:
            dict: A dictionary containing:
                - message (str): Success message indicating the project was deleted.
                - data (dict): Dictionary containing the deleted project's id and project_id.
        Raises:
            HTTPException:
                - status_code 404: If the project with the given project_id does not exist.
                - status_code 500: If an unexpected error occurs during deletion.
        Note:
            - Requires user to have Project Manager privileges.
            - All database changes are rolled back if an error occurs.
            - Deletion is logged with the PM's email for audit purposes.
        """
        try:
            logger.info(f"Deleting project {project_id} by {current_user.email}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            deleted_project_id = project.project_id
            deleted_id = project.id

            session.delete(project)
            session.commit()

            return {
                "message": "Project deleted successfully",
                "data": {
                    "id": deleted_id,
                    "project_id": deleted_project_id,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting project: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


class ProjectsDashboardResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve dashboard data for all projects including associated clients and requirements count.

        Fetches comprehensive project information including client details and the number of requirements
        associated with each project. Only accessible by users with Project Manager (PM) role.

        Args:
            current_user (User): The authenticated user making the request, must have PM role.
            Obtained via dependency injection using `require_pm()`.
            session (Session): Database session for executing queries.
            Obtained via dependency injection using `get_session()`.

        Returns:
            dict: A dictionary containing:
            - message (str): Success message indicating dashboard data was retrieved.
            - data (dict): Contains:
                - projects (list): List of project dictionaries, each containing:
                - id (int): Project unique identifier
                - project_id (str): Project ID
                - project_name (str): Name of the project
                - description (str): Project description
                - status (str): Current status of the project
                - client (dict): Client information including:
                    - id (int): Client ID
                    - name (str): Client name
                    - email (str): Client email
                - requirements_count (int): Total number of requirements for the project
                - total_projects (int): Total number of projects

        Raises:
            HTTPException: Status code 500 if an error occurs during data retrieval.

        Logs:
            - Info: Logs the user email when fetching dashboard data begins.
            - Error: Logs any exceptions that occur during the retrieval process.
        """
        try:
            logger.info(f"Fetching project dashboard data by {current_user.email}")

            statement = select(Project)
            projects = session.exec(statement).all()

            project_list = []
            for project in projects:

                client = session.exec(
                    select(Client).where(Client.id == project.client_id)
                ).first()

                requirements_count = len(
                    session.exec(
                        select(Requirement).where(Requirement.project_id == project.id)
                    ).all()
                )

                project_data = {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "status": project.status,
                    "client": (
                        {
                            "id": client.client_id if client else None,
                            "name": client.client_name if client else None,
                            "email": client.email if client else None,
                        }
                        if client
                        else None
                    ),
                    "requirements_count": requirements_count,
                }
                project_list.append(project_data)

            return {
                "message": "Dashboard data retrieved successfully",
                "data": {
                    "projects": project_list,
                    "total_projects": len(project_list),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching dashboard data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


class ProjectViewResource(Resource):
    """This class is responsible to show the data for individual project view, edit path and delete path"""

    def get(
        self,
        project_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve detailed information for a specific project by its ID.

        Fetches comprehensive details of a single project including associated client information,
        requirements, and updates linked to the project. Only accessible by users with Project Manager (PM) role.

        Args:
            project_id (int): The unique identifier of the project to retrieve.
            current_user (User): The authenticated user making the request, must have PM role.
            session (Session): Database session for executing queries.

        Returns:
            dict: A dictionary containing:
                - message (str): Success message indicating project data was retrieved.
                - data (dict): Contains project details, client info, requirements, and updates

        Raises:
            HTTPException:
                - Status code 404 if the project with the given project_id does not exist.
                - Status code 500 if an error occurs during data retrieval.
        """

        try:
            logger.info(f"Fetching project {project_id} data by {current_user.email}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            client = session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            requirements = session.exec(
                select(Requirement).where(Requirement.project_id == project.id)
            ).all()

            requirement_list = [
                {
                    "id": req.id,
                    "requirement_id": req.requirement_id,
                    "requirements": req.requirements,
                    "status": req.status,
                    "client_id": req.client_id,
                }
                for req in requirements
            ]

            updates = session.exec(
                select(Update).where(Update.project_id == project.id)
            ).all()

            update_list = [
                {
                    "id": update.id,
                    "update_id": update.update_id,
                    "details": update.details,
                    "date": update.date.isoformat(),
                    "created_by": update.created_by,
                }
                for update in updates
            ]

            project_data = {
                "id": project.id,
                "project_id": project.project_id,
                "project_name": project.project_name,
                "description": project.description,
                "status": project.status,
                "manager_id": project.manager_id,
                "client": (
                    {
                        "id": client.id if client else None,
                        "client_id": client.client_id if client else None,
                        "name": client.client_name if client else None,
                        "email": client.email if client else None,
                    }
                    if client
                    else None
                ),
                "requirements": requirement_list,
                "requirements_count": len(requirement_list),
                "updates": update_list,
                "updates_count": len(update_list),
            }

            return {
                "message": "Project data retrieved successfully",
                "data": project_data,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching project data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        project_id: int,
        data: ProjectUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Update an existing project with the provided details.

        Args:
            project_id (int): The ID of the project to update.
            data (ProjectUpdateModel): The project data to update containing optional fields:
                - project_name (str, optional): New project name
                - description (str, optional): New project description
                - status (StatusTypeEnum, optional): New project status
                - manager_id (int, optional): New project manager ID
            current_user (User): The currently authenticated user (must be a project manager).
            session (Session): The database session for executing queries.

        Returns:
            dict: A dictionary containing the updated project information with requirements and updates.

        Raises:
            HTTPException:
                - 404 if project with given project_id is not found
                - 404 if manager_id is provided but the manager user is not found
                - 500 if an internal server error occurs during the update process
        """
        try:
            logger.info(f"Updating project {project_id} by {current_user.email}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            if data.project_name is not None:
                project.project_name = data.project_name
            if data.description is not None:
                project.description = data.description
            if data.status is not None:
                project.status = data.status
            if data.manager_id is not None:

                manager = session.exec(
                    select(User).where(User.id == data.manager_id)
                ).first()
                if not manager:
                    raise HTTPException(status_code=404, detail="Manager not found")
                project.manager_id = data.manager_id

            session.add(project)
            session.commit()
            session.refresh(project)

            client = session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            requirements = session.exec(
                select(Requirement).where(Requirement.project_id == project.id)
            ).all()

            requirement_list = [
                {
                    "id": req.id,
                    "requirement_id": req.requirement_id,
                    "requirements": req.requirements,
                    "status": req.status,
                }
                for req in requirements
            ]

            updates = session.exec(
                select(Update).where(Update.project_id == project.id)
            ).all()

            update_list = [
                {
                    "id": update.id,
                    "update_id": update.update_id,
                    "details": update.details,
                    "date": update.date.isoformat(),
                }
                for update in updates
            ]

            return {
                "message": "Project updated successfully",
                "data": {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "status": project.status,
                    "manager_id": project.manager_id,
                    "client": (
                        {
                            "id": client.id if client else None,
                            "client_id": client.client_id if client else None,
                            "name": client.client_name if client else None,
                            "email": client.email if client else None,
                        }
                        if client
                        else None
                    ),
                    "requirements": requirement_list,
                    "updates": update_list,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating project: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def patch(
        self,
        project_id: int,
        data: ProjectUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Partially update an existing project with the provided details.
        This is an alias for PUT method for PATCH HTTP verb support.

        Args:
            project_id (int): The ID of the project to update.
            data (ProjectUpdateModel): The project data to update containing optional fields.
            current_user (User): The currently authenticated user (must be a project manager).
            session (Session): The database session for executing queries.

        Returns:
            dict: A dictionary containing the updated project information.
        """
        return self.put(project_id, data, current_user, session)

    def delete(
        self,
        project_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a project by its ID.

        This endpoint allows a Project Manager to delete a project from the system.
        Also deletes all associated requirements and updates.

        Args:
            project_id (int): The unique identifier of the project to be deleted.
            current_user (User): The authenticated user performing the delete operation.
            session (Session): The database session for executing queries and transactions.

        Returns:
            dict: A dictionary containing success message and deleted project details.

        Raises:
            HTTPException:
                - status_code 404: If the project with the given project_id does not exist.
                - status_code 500: If an unexpected error occurs during deletion.
        """
        try:
            logger.info(f"Deleting project {project_id} by {current_user.email}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            requirements_count = len(
                session.exec(
                    select(Requirement).where(Requirement.project_id == project.id)
                ).all()
            )
            updates_count = len(
                session.exec(
                    select(Update).where(Update.project_id == project.id)
                ).all()
            )

            deleted_project_id = project.project_id
            deleted_id = project.id

            requirements = session.exec(
                select(Requirement).where(Requirement.project_id == project.id)
            ).all()
            for req in requirements:
                session.delete(req)

            updates = session.exec(
                select(Update).where(Update.project_id == project.id)
            ).all()
            for update in updates:
                session.delete(update)

            session.delete(project)
            session.commit()

            return {
                "message": "Project and associated data deleted successfully",
                "data": {
                    "id": deleted_id,
                    "project_id": deleted_project_id,
                    "deleted_requirements": requirements_count,
                    "deleted_updates": updates_count,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting project: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
