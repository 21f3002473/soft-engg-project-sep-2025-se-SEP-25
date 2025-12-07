"""
REST API Resource for client progress email management.
Handles email generation, history retrieval, and sending operations.
"""

import logging
from typing import Optional
from datetime import datetime

from app.database import User, get_session
from app.database.product_manager_models import (
    ClientProgressEmail,
    Project,
    Client,
)
from app.middleware import require_pm
from app.tasks.requirement_tasks import generate_progress_email_task
from fastapi import Depends, HTTPException, Query
from fastapi_restful import Resource
from sqlmodel import Session, select, desc

logger = logging.getLogger(__name__)


class ProjectProgressEmailResource(Resource):
    """
    API Resource for client progress email generation and retrieval.

    Endpoints:
    - GET: Get all progress emails for a project
    - POST: Trigger progress email generation
    """

    def get(
        self,
        project_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get all progress emails sent for a project.

        Args:
            project_id: Project ID
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: List of progress emails with metadata
        """
        try:

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            emails = session.exec(
                select(ClientProgressEmail)
                .where(ClientProgressEmail.project_id == project_id)
                .order_by(desc(ClientProgressEmail.sent_at))
            ).all()

            email_list = []
            for email in emails:
                email_list.append(
                    {
                        "id": email.id,
                        "subject": email.subject,
                        "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                        "trigger_type": email.trigger_type,
                        "recipient_email": email.recipient_email,
                        "delivery_status": email.delivery_status,
                        "opened": email.opened,
                        "opened_at": (
                            email.opened_at.isoformat() if email.opened_at else None
                        ),
                        "project_status": email.project_status,
                    }
                )

            return {
                "message": "Email history retrieved successfully",
                "project_id": project_id,
                "project_name": project.project_name,
                "total_emails": len(email_list),
                "emails": email_list,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching email history: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch email history: {str(e)}"
            )

    def post(
        self,
        project_id: int,
        auto_send: bool = Query(True, description="Automatically send the email"),
        trigger_type: str = Query("manual", description="What triggered this email"),
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Trigger AI generation of a progress email for the project.

        Args:
            project_id: Project ID
            auto_send: Whether to automatically send the email
            trigger_type: What triggered this email generation
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Task status and job ID
        """
        try:
            logger.info(
                f"Progress email generation requested for project {project_id} by {current_user.email}"
            )

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            client = session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            if not client:
                raise HTTPException(
                    status_code=404, detail="Client not found for this project"
                )

            task = generate_progress_email_task.delay(
                project_id=project_id,
                client_id=client.id,
                trigger_type=trigger_type,
                auto_send=auto_send,
            )

            return {
                "message": "Progress email generation started",
                "task_id": task.id,
                "project_id": project_id,
                "project_name": project.project_name,
                "client_email": client.email,
                "auto_send": auto_send,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating progress email: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to generate progress email: {str(e)}"
            )


class ProgressEmailDetailResource(Resource):
    """
    API Resource for individual progress email details.

    Endpoints:
    - GET: Get full details of a specific email including content
    """

    def get(
        self,
        email_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get full details of a specific progress email including content.

        Args:
            email_id: Email ID
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Complete email details including HTML and text content
        """
        try:

            email = session.exec(
                select(ClientProgressEmail).where(ClientProgressEmail.id == email_id)
            ).first()

            if not email:
                raise HTTPException(status_code=404, detail="Email not found")

            project = session.exec(
                select(Project).where(Project.id == email.project_id)
            ).first()

            client = session.exec(
                select(Client).where(Client.id == email.client_id)
            ).first()

            return {
                "message": "Email details retrieved successfully",
                "email": {
                    "id": email.id,
                    "subject": email.subject,
                    "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                    "trigger_type": email.trigger_type,
                    "recipient_email": email.recipient_email,
                    "cc_emails": email.cc_emails,
                    "delivery_status": email.delivery_status,
                    "opened": email.opened,
                    "opened_at": (
                        email.opened_at.isoformat() if email.opened_at else None
                    ),
                    "email_body_text": email.email_body_text,
                    "email_body_html": email.email_body_html,
                    "update_ids": email.update_ids,
                    "project_status": email.project_status,
                },
                "project": (
                    {
                        "id": project.id,
                        "project_name": project.project_name,
                        "project_id": project.project_id,
                    }
                    if project
                    else None
                ),
                "client": (
                    {
                        "id": client.id,
                        "client_name": client.client_name,
                        "email": client.email,
                    }
                    if client
                    else None
                ),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching email details: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch email details: {str(e)}"
            )
