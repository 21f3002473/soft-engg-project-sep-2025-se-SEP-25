"""
API Resources for Project Daily Reports
Handles fetching and generating daily progress reports
"""

import logging
from datetime import datetime
from typing import Optional

from app.database import User, get_session
from app.database.product_manager_models import Client, Project, ProjectDailyReport
from app.middleware import require_pm
from app.tasks.requirement_tasks import generate_daily_project_report
from fastapi import Depends, HTTPException, Query
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from sqlmodel import Session, desc, select

logger = logging.getLogger(__name__)

router = InferringRouter()


@cbv(router)
class ProjectDailyReportsResource:
    """
    API Resource for project daily reports list.

    Endpoints:
    - GET: Fetch all daily reports for a project
    - POST: Trigger manual daily report generation
    """

    def get(
        self,
        project_id: int,
        limit: int = Query(30, description="Number of reports to fetch"),
        offset: int = Query(0, description="Number of reports to skip"),
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get list of daily reports for a project.

        Args:
            project_id: Project ID
            limit: Number of reports to return
            offset: Number of reports to skip
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: List of daily reports
        """
        try:
            logger.info(f"Fetching daily reports for project {project_id}")

            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            query = (
                select(ProjectDailyReport)
                .where(ProjectDailyReport.project_id == project_id)
                .order_by(desc(ProjectDailyReport.report_date))
                .offset(offset)
                .limit(limit)
            )

            reports = session.exec(query).all()

            count_query = select(ProjectDailyReport).where(
                ProjectDailyReport.project_id == project_id
            )
            total_count = len(session.exec(count_query).all())

            reports_data = [
                {
                    "id": report.id,
                    "report_date": (
                        report.report_date.isoformat() if report.report_date else None
                    ),
                    "generated_at": (
                        report.generated_at.isoformat() if report.generated_at else None
                    ),
                    "summary": report.summary,
                    "updates_count": report.updates_count,
                    "completion_percentage": report.completion_percentage,
                    "email_sent": report.email_sent,
                    "trigger_type": report.trigger_type,
                }
                for report in reports
            ]

            return {
                "message": "Daily reports fetched successfully",
                "data": reports_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching daily reports: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch daily reports: {str(e)}"
            )

    def post(
        self,
        project_id: int,
        auto_send: bool = Query(
            True, description="Automatically send the report via email"
        ),
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Trigger manual generation of a daily report.

        Args:
            project_id: Project ID
            auto_send: Whether to send report via email
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Task status and job ID
        """
        try:
            logger.info(
                f"Daily report generation requested for project {project_id} by {current_user.email}"
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

            task = generate_daily_project_report.delay(
                project_id=project_id, client_id=client.id, auto_send=auto_send
            )

            return {
                "message": "Daily report generation started",
                "task_id": task.id,
                "project_id": project_id,
                "project_name": project.project_name,
                "client_email": client.email,
                "auto_send": auto_send,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to generate daily report: {str(e)}"
            )


@cbv(router)
class DailyReportDetailResource:
    """
    API Resource for individual daily report details.

    Endpoints:
    - GET: Get full details of a specific daily report
    """

    def get(
        self,
        report_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get full details of a specific daily report including content.

        Args:
            report_id: Report ID
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Complete report details including HTML and text content
        """
        try:

            report = session.exec(
                select(ProjectDailyReport).where(ProjectDailyReport.id == report_id)
            ).first()

            if not report:
                raise HTTPException(status_code=404, detail="Report not found")

            project = session.exec(
                select(Project).where(Project.id == report.project_id)
            ).first()

            client = session.exec(
                select(Client).where(Client.id == report.client_id)
            ).first()

            import json

            try:
                achievements = (
                    json.loads(report.achievements) if report.achievements else []
                )
            except:
                achievements = []

            try:
                blockers = json.loads(report.blockers) if report.blockers else []
            except:
                blockers = []

            try:
                upcoming_tasks = (
                    json.loads(report.upcoming_tasks) if report.upcoming_tasks else []
                )
            except:
                upcoming_tasks = []

            try:
                metrics = json.loads(report.metrics) if report.metrics else {}
            except:
                metrics = {}

            return {
                "message": "Report details retrieved successfully",
                "report": {
                    "id": report.id,
                    "report_date": (
                        report.report_date.isoformat() if report.report_date else None
                    ),
                    "generated_at": (
                        report.generated_at.isoformat() if report.generated_at else None
                    ),
                    "trigger_type": report.trigger_type,
                    "summary": report.summary,
                    "achievements": achievements,
                    "blockers": blockers,
                    "upcoming_tasks": upcoming_tasks,
                    "metrics": metrics,
                    "report_body_text": report.report_body_text,
                    "report_body_html": report.report_body_html,
                    "email_sent": report.email_sent,
                    "email_sent_at": (
                        report.email_sent_at.isoformat()
                        if report.email_sent_at
                        else None
                    ),
                    "recipient_email": report.recipient_email,
                    "email_delivery_status": report.email_delivery_status,
                    "updates_count": report.updates_count,
                    "completion_percentage": report.completion_percentage,
                },
                "project": {
                    "id": project.id if project else None,
                    "project_id": project.project_id if project else None,
                    "project_name": project.project_name if project else None,
                    "status": project.status.value if project else None,
                },
                "client": {
                    "id": client.id if client else None,
                    "client_id": client.client_id if client else None,
                    "client_name": client.client_name if client else None,
                    "email": client.email if client else None,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching report details: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch report details: {str(e)}"
            )
