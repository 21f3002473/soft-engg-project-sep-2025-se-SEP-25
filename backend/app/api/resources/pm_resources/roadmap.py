"""
API Resource for project roadmap generation and retrieval.
"""

from logging import getLogger
from typing import Optional
import json

from app.database import User, get_session
from app.database.product_manager_models import RequirementRoadmap, Project, Client
from app.middleware import require_pm
from app.tasks.requirement_tasks import generate_project_roadmap_task
from app.core.agents.pm_agents.pm_roadmap_agent import get_pm_roadmap_agent
from fastapi import Depends, HTTPException, Query
from fastapi_restful import Resource
from pydantic import BaseModel
from sqlmodel import Session, select, desc

logger = getLogger(__name__)


class RoadmapGenerateRequest(BaseModel):
    """Request model for roadmap generation."""

    notify_email: Optional[str] = None
    send_email: bool = True
    trigger_type: str = "manual"


class ProjectRoadmapResource(Resource):
    """
    API Resource for AI-powered project roadmap generation.

    Endpoints:
    - GET: Get current roadmap for a project
    - POST: Trigger roadmap generation (async or sync)
    """

    def get(
        self,
        project_id: int,
        client_id: int,
        version: Optional[int] = Query(
            None, description="Specific version to retrieve"
        ),
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Get the current or specific version of project roadmap.

        Args:
            project_id: Project ID
            client_id: Client ID
            version: Optional specific version number
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Roadmap data
        """
        try:
            logger.info(
                f"Fetching roadmap for project {project_id}, client {client_id} by {current_user.email}"
            )

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            query = select(RequirementRoadmap).where(
                RequirementRoadmap.project_id == project_id,
                RequirementRoadmap.client_id == client_id,
            )

            if version:
                query = query.where(RequirementRoadmap.version == version)
            else:
                query = query.where(RequirementRoadmap.is_current == True)

            roadmap = session.exec(query).first()

            if not roadmap:

                logger.info(f"No roadmap found, generating new roadmap")
                agent = get_pm_roadmap_agent(session)
                roadmap_data = agent.generate_roadmap(project_id)

                if "error" in roadmap_data:
                    raise HTTPException(status_code=500, detail=roadmap_data["error"])

                saved_roadmap = agent.save_roadmap(
                    roadmap=roadmap_data,
                    client_id=client_id,
                    trigger_type="auto_generated",
                    generated_by=current_user.id,
                )

                return {
                    "message": "Roadmap generated successfully",
                    "data": {
                        **roadmap_data,
                        "id": saved_roadmap.id,
                        "version": saved_roadmap.version,
                        "is_current": saved_roadmap.is_current,
                        "generated_at": saved_roadmap.generated_at.isoformat(),
                        "trigger_type": saved_roadmap.trigger_type,
                    },
                    "is_new": True,
                }

            roadmap_data = json.loads(roadmap.roadmap_data)

            return {
                "message": "Roadmap retrieved successfully",
                "data": {
                    **roadmap_data,
                    "id": roadmap.id,
                    "version": roadmap.version,
                    "is_current": roadmap.is_current,
                    "generated_at": roadmap.generated_at.isoformat(),
                    "trigger_type": roadmap.trigger_type,
                },
                "is_new": False,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching roadmap: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Roadmap retrieval error: {str(e)}"
            )

    def post(
        self,
        project_id: int,
        client_id: int,
        request_data: Optional[RoadmapGenerateRequest] = None,
        async_generation: bool = Query(False, description="Generate asynchronously"),
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Generate a new project roadmap.

        Args:
            project_id: Project ID
            client_id: Client ID
            request_data: Optional request body
            async_generation: Whether to generate asynchronously
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Generation status and roadmap data
        """
        try:
            logger.info(
                f"Roadmap generation requested for project {project_id} by {current_user.email}"
            )

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            client = session.exec(select(Client).where(Client.id == client_id)).first()

            if not client:
                raise HTTPException(status_code=404, detail="Client not found")

            trigger_type = request_data.trigger_type if request_data else "manual"
            send_email = request_data.send_email if request_data else True
            notify_email = (
                (
                    request_data.notify_email
                    if request_data and request_data.notify_email
                    else current_user.email
                )
                if send_email
                else None
            )

            if async_generation:

                task = generate_project_roadmap_task.delay(
                    project_id=project_id,
                    client_id=client_id,
                    trigger_type=trigger_type,
                    notify_email=notify_email,
                )

                message = "Roadmap generation started."
                if notify_email:
                    message += f" Results will be sent to {notify_email}."

                return {
                    "message": message,
                    "data": {
                        "task_id": task.id,
                        "project_id": project_id,
                        "client_id": client_id,
                        "status": "processing",
                    },
                }
            else:

                agent = get_pm_roadmap_agent(session)
                roadmap = agent.generate_roadmap(project_id)

                if "error" in roadmap:
                    raise HTTPException(status_code=500, detail=roadmap["error"])

                saved_roadmap = agent.save_roadmap(
                    roadmap=roadmap,
                    client_id=client_id,
                    trigger_type=trigger_type,
                    generated_by=current_user.id,
                )

                if notify_email:
                    from app.tasks.requirement_tasks import send_roadmap_email

                    send_roadmap_email.delay(roadmap, notify_email)

                return {
                    "message": "Roadmap generated successfully",
                    "data": roadmap,
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate roadmap")


class RoadmapHistoryResource(Resource):
    """
    API Resource for roadmap version history.
    """

    def get(
        self,
        project_id: int,
        client_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Get all roadmap versions for a project.

        Args:
            project_id: Project ID
            client_id: Client ID
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: List of roadmap versions
        """
        try:
            logger.info(
                f"Fetching roadmap history for project {project_id} by {current_user.email}"
            )

            roadmaps = session.exec(
                select(RequirementRoadmap)
                .where(
                    RequirementRoadmap.project_id == project_id,
                    RequirementRoadmap.client_id == client_id,
                )
                .order_by(desc(RequirementRoadmap.version))
            ).all()

            history = [
                {
                    "id": rm.id,
                    "version": rm.version,
                    "generated_at": rm.generated_at.isoformat(),
                    "trigger_type": rm.trigger_type,
                    "is_current": rm.is_current,
                    "summary": rm.summary,
                    "estimated_completion_days": rm.estimated_completion_days,
                    "email_sent": rm.email_sent,
                }
                for rm in roadmaps
            ]

            return {
                "message": "Roadmap history retrieved successfully",
                "data": {
                    "history": history,
                    "total_versions": len(history),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching roadmap history: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Failed to fetch roadmap history"
            )
