from logging import getLogger
from typing import Optional

from app.database import User, get_session
from app.database.product_manager_models import Client, Project, Requirement, Update
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


class ClientUpdateModel(BaseModel):
    client_name: Optional[str] = None
    email: Optional[str] = None
    image_base64: Optional[str] = None


class RequirementCreateModel(BaseModel):
    requirement_id: str
    requirements: str
    project_id: str  # Changed to str to accept project_id like "PRJ001"


class RequirementUpdateModel(BaseModel):
    requirements: Optional[str] = None
    project_id: Optional[str] = None  # Changed to str


class UpdateCreateModel(BaseModel):
    update_id: str
    project_id: int
    details: Optional[str] = None


class UpdateUpdateModel(BaseModel):
    details: Optional[str] = None


class ClientsResource(Resource):
    """
    ClientsResource

    A REST resource for managing clients. Provides CRUD operations for client data.

    This resource requires the current user to have Project Manager (PM) permissions
    for all operations.

    Methods:
        get: Retrieve all clients from the database
        post: Create a new client with the provided details
        put: Update an existing client's information
        delete: Remove a client from the database

    Dependencies:
        - current_user: Authenticated user with PM role (required for all methods)
        - session: Database session for executing queries

    Raises:
        HTTPException: 400 - Client ID already exists (POST)
        HTTPException: 404 - Client not found (PUT, DELETE)
        HTTPException: 500 - Internal server error

    """

    def get(
        self,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Get all clients"""
        try:
            logger.info(f"Fetching all clients by {current_user.email}")

            statement = select(Client)
            clients = session.exec(statement).all()

            client_list = [
                {
                    "id": client.id,
                    "client_id": client.client_id,
                    "client_name": client.client_name,
                    "email": client.email,
                    "image": client.image_base64,
                }
                for client in clients
            ]

            return {
                "message": "Clients retrieved successfully",
                "data": {
                    "clients": client_list,
                    "total_clients": len(client_list),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching clients: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def post(
        self,
        data: ClientCreateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Create a new client"""
        try:
            logger.info(f"Creating client by {current_user.email}")

            existing = session.exec(
                select(Client).where(Client.client_id == data.client_id)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Client ID already exists")

            new_client = Client(
                client_id=data.client_id,
                client_name=data.client_name,
                email=data.email,
                image_base64=data.image_base64,
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
                },
            }

        except HTTPException:
            raise
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error creating client: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Database integrity error. Please contact administrator to reset the sequence.",
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating client: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        client_id: int,
        data: ClientUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Update a client"""
        try:
            logger.info(f"Updating client {client_id} by {current_user.email}")

            client = session.exec(select(Client).where(Client.id == client_id)).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            if data.client_name is not None:
                client.client_name = data.client_name
            if data.email is not None:
                client.email = data.email
            if data.image_base64 is not None:
                client.image_base64 = data.image_base64

            session.add(client)
            session.commit()
            session.refresh(client)

            return {
                "message": "Client updated successfully",
                "data": {
                    "id": client.id,
                    "client_id": client.client_id,
                    "client_name": client.client_name,
                    "email": client.email,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating client: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(
        self,
        client_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Delete a client"""
        try:
            logger.info(f"Deleting client {client_id} by {current_user.email}")

            client = session.exec(select(Client).where(Client.id == client_id)).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            session.delete(client)
            session.commit()

            return {
                "message": "Client deleted successfully",
                "data": {"id": client_id},
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting client: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


class ClientRequirementResource(Resource):
    """
    Resource class for managing client requirements in the project management system.

    This resource provides CRUD operations for client requirements, allowing project
    managers to create, retrieve, update, and delete requirements associated with
    specific clients.

    Methods:
        get(client_id, current_user, session):
            Retrieves all requirements for a specific client along with client details.
            Returns client information and a list of associated requirements.

        post(client_id, data, current_user, session):
            Creates a new requirement for a specified client. Validates that the client
            exists and that the requirement ID is unique before creation.

        put(client_id, requirement_id, data, current_user, session):
            Updates an existing requirement's details such as description and project ID.
            Ensures the requirement belongs to the specified client before updating.

        delete(client_id, requirement_id, current_user, session):
            Deletes a requirement from a specific client. Verifies the requirement
            exists and belongs to the client before deletion.

    Access Control:
        All methods require project manager (PM) role authentication via require_pm().

    Database:
        Uses SQLAlchemy ORM for database operations with automatic session management.
        Includes transaction rollback on errors for data consistency.

    Logging:
        All operations are logged with user email and relevant identifiers for
        audit trail and debugging purposes.
    """

    def get(
        self,
        client_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Get requirements for a specific client"""
        try:
            logger.info(
                f"Fetching requirements for client {client_id} by {current_user.email}"
            )

            client_statement = select(Client).where(Client.id == client_id)
            client = session.exec(client_statement).first()

            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            requirement_statement = select(Requirement).where(
                Requirement.client_id == client_id
            )
            requirements = session.exec(requirement_statement).all()

            requirement_list = [
                {
                    "id": req.id,
                    "requirement_id": req.requirement_id,
                    "description": req.requirements,
                    "project_id": req.project_id,
                    "status": req.status,
                }
                for req in requirements
            ]

            return {
                "message": "Requirements retrieved successfully",
                "data": {
                    "client": {
                        "id": client.id,
                        "client_id": client.client_id,
                        "client_name": client.client_name,
                        "email": client.email,
                        "image": client.image_base64,
                    },
                    "requirements": requirement_list,
                    "total_requirements": len(requirement_list),
                },
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching requirements: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def post(
        self,
        client_id: int,
        data: RequirementCreateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Create a new requirement for a client"""
        try:
            logger.info(
                f"Creating requirement for client {client_id} by {current_user.email}"
            )

            client = session.exec(select(Client).where(Client.id == client_id)).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            existing = session.exec(
                select(Requirement).where(
                    Requirement.requirement_id == data.requirement_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, detail="Requirement ID already exists"
                )

            # Find project by project_id (string) to get the actual id (int)
            project = session.exec(
                select(Project).where(Project.project_id == data.project_id)
            ).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            new_requirement = Requirement(
                requirement_id=data.requirement_id,
                requirements=data.requirements,
                project_id=project.id,  # Use the integer id from the project
                client_id=client_id,
            )
            session.add(new_requirement)
            session.commit()
            session.refresh(new_requirement)

            return {
                "message": "Requirement created successfully",
                "data": {
                    "id": new_requirement.id,
                    "requirement_id": new_requirement.requirement_id,
                    "description": new_requirement.requirements,
                    "project_id": data.project_id,  # Return the string project_id
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating requirement: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        client_id: int,
        requirement_id: int,
        data: RequirementUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Update a requirement"""
        try:
            logger.info(
                f"Updating requirement {requirement_id} by {current_user.email}"
            )

            requirement = session.exec(
                select(Requirement).where(
                    Requirement.id == requirement_id, Requirement.client_id == client_id
                )
            ).first()
            if not requirement:
                raise HTTPException(status_code=404, detail="Requirement not found")

            if data.requirements is not None:
                requirement.requirements = data.requirements
            if data.project_id is not None:
                # Find project by project_id (string) to get the actual id (int)
                project = session.exec(
                    select(Project).where(Project.project_id == data.project_id)
                ).first()
                if not project:
                    raise HTTPException(status_code=404, detail="Project not found")
                requirement.project_id = project.id

            session.add(requirement)
            session.commit()
            session.refresh(requirement)

            return {
                "message": "Requirement updated successfully",
                "data": {
                    "id": requirement.id,
                    "requirement_id": requirement.requirement_id,
                    "description": requirement.requirements,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating requirement: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(
        self,
        client_id: int,
        requirement_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Delete a requirement"""
        try:
            logger.info(
                f"Deleting requirement {requirement_id} by {current_user.email}"
            )

            requirement = session.exec(
                select(Requirement).where(
                    Requirement.id == requirement_id, Requirement.client_id == client_id
                )
            ).first()
            if not requirement:
                raise HTTPException(status_code=404, detail="Requirement not found")

            session.delete(requirement)
            session.commit()

            return {
                "message": "Requirement deleted successfully",
                "data": {"id": requirement_id},
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting requirement: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


class ClientUpdatesResource(Resource):
    """
    Resource class for managing client updates.

    This class provides REST API endpoints for retrieving, creating, updating, and deleting
    updates associated with a specific client's projects. All operations require PM-level
    authorization and maintain proper audit logging.

    Methods:
        get(client_id, current_user, session): Retrieves all updates for a specific client
            across all their projects. Returns client details and a list of formatted updates.

        post(client_id, data, current_user, session): Creates a new update for a project
            belonging to the specified client. Validates that the project belongs to the client
            before creation.

        put(client_id, update_id, data, current_user, session): Updates an existing update
            record. Validates that the update belongs to one of the client's projects.

        delete(client_id, update_id, current_user, session): Deletes an update record.
            Validates that the update belongs to one of the client's projects before deletion.

    Authorization:
        All methods require PM (Project Manager) role authorization via require_pm() dependency.

    Database:
        All methods use SQLAlchemy Session for database operations with proper transaction
        management, including rollback on errors.

    Logging:
        All operations are logged with user email, operation details, and error information
        where applicable.
    """

    def get(
        self,
        client_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Get updates for a specific client"""
        try:
            logger.info(
                f"Fetching updates for client {client_id} by {current_user.email}"
            )

            client_statement = select(Client).where(Client.id == client_id)
            client = session.exec(client_statement).first()

            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            project_statement = select(Project).where(Project.client_id == client_id)
            projects = session.exec(project_statement).all()
            project_ids = [p.id for p in projects]

            updates = []
            if project_ids:
                update_statement = select(Update).where(
                    Update.project_id.in_(project_ids)
                )
                updates = session.exec(update_statement).all()

            update_list = [
                {
                    "id": update.id,
                    "update_id": update.update_id,
                    "description": update.details
                    or f"Description of update {update.update_id}",
                    "date": update.date.isoformat(),
                    "project_id": update.project_id,
                    "created_by": update.created_by,
                }
                for update in updates
            ]

            return {
                "message": "Updates retrieved successfully",
                "data": {
                    "client": {
                        "id": client.id,
                        "client_id": client.client_id,
                        "client_name": client.client_name,
                        "email": client.email,
                        "image": client.image_base64,
                    },
                    "updates": update_list,
                    "total_updates": len(update_list),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching client updates: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def post(
        self,
        client_id: int,
        data: UpdateCreateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Create a new update for a client project"""
        try:
            logger.info(
                f"Creating update for client {client_id} by {current_user.email}"
            )

            client = session.exec(select(Client).where(Client.id == client_id)).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            project = session.exec(
                select(Project).where(
                    Project.id == data.project_id, Project.client_id == client_id
                )
            ).first()
            if not project:
                raise HTTPException(
                    status_code=404, detail="Project not found for this client"
                )

            new_update = Update(
                update_id=data.update_id,
                project_id=data.project_id,
                created_by=current_user.id,
                details=data.details,
            )
            session.add(new_update)
            session.commit()
            session.refresh(new_update)

            return {
                "message": "Update created successfully",
                "data": {
                    "id": new_update.id,
                    "update_id": new_update.update_id,
                    "description": new_update.details,
                    "date": new_update.date.isoformat(),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating update: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        client_id: int,
        update_id: int,
        data: UpdateUpdateModel,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Update an update"""
        try:
            logger.info(f"Updating update {update_id} by {current_user.email}")

            update = session.exec(
                select(Update)
                .join(Project)
                .where(Update.id == update_id, Project.client_id == client_id)
            ).first()
            if not update:
                raise HTTPException(status_code=404, detail="Update not found")

            if data.details is not None:
                update.details = data.details

            session.add(update)
            session.commit()
            session.refresh(update)

            return {
                "message": "Update updated successfully",
                "data": {
                    "id": update.id,
                    "update_id": update.update_id,
                    "description": update.details,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating update: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(
        self,
        client_id: int,
        update_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Delete an update"""
        try:
            logger.info(f"Deleting update {update_id} by {current_user.email}")

            update = session.exec(
                select(Update)
                .join(Project)
                .where(Update.id == update_id, Project.client_id == client_id)
            ).first()
            if not update:
                raise HTTPException(status_code=404, detail="Update not found")

            session.delete(update)
            session.commit()

            return {
                "message": "Update deleted successfully",
                "data": {"id": update_id},
            }

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting update: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
