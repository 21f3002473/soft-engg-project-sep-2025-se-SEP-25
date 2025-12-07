"""
API Resources for Employee Daily Reports
Handles fetching and generating daily performance reports for employees
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from sqlmodel import Session, select, desc

from app.middleware import require_pm
from app.database import get_session
from app.database import User
from app.database.product_manager_models import EmployeeDailyReport
from app.tasks.requirement_tasks import generate_employee_daily_report

logger = logging.getLogger(__name__)

router = InferringRouter()


@cbv(router)
class EmployeeDailyReportsResource:
    """
    API Resource for employee daily reports list.

    Endpoints:
    - GET: Fetch all daily reports for an employee
    - POST: Trigger manual daily report generation
    """

    def get(
        self,
        employee_id: int,
        limit: int = Query(30, description="Number of reports to fetch"),
        offset: int = Query(0, description="Number of reports to skip"),
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get list of daily reports for an employee.

        Args:
            employee_id: Employee ID
            limit: Number of reports to return
            offset: Number of reports to skip
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: List of daily reports
        """
        try:
            logger.info(f"Fetching daily reports for employee {employee_id}")

            employee = session.exec(select(User).where(User.id == employee_id)).first()

            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")

            query = (
                select(EmployeeDailyReport)
                .where(EmployeeDailyReport.employee_id == employee_id)
                .order_by(desc(EmployeeDailyReport.report_date))
                .offset(offset)
                .limit(limit)
            )

            reports = session.exec(query).all()

            count_query = select(EmployeeDailyReport).where(
                EmployeeDailyReport.employee_id == employee_id
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
                    "tasks_completed_today": report.tasks_completed_today,
                    "productivity_score": report.productivity_score,
                    "projects_worked_on": report.projects_worked_on,
                    "email_sent": report.email_sent,
                    "trigger_type": report.trigger_type,
                }
                for report in reports
            ]

            return {
                "message": "Employee reports fetched successfully",
                "data": reports_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "employee": {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "role": employee.role,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching employee reports: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch employee reports: {str(e)}"
            )

    def post(
        self,
        employee_id: int,
        auto_send: bool = Query(
            True, description="Automatically send the report via email"
        ),
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Trigger manual generation of an employee daily report.

        Args:
            employee_id: Employee ID
            auto_send: Whether to send report via email
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Task status and job ID
        """
        try:
            logger.info(
                f"Employee report generation requested for employee {employee_id} by {current_user.email}"
            )

            employee = session.exec(select(User).where(User.id == employee_id)).first()

            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")

            task = generate_employee_daily_report.delay(
                employee_id=employee_id, auto_send=auto_send
            )

            return {
                "message": "Employee report generation started",
                "task_id": task.id,
                "employee_id": employee_id,
                "employee_name": employee.name,
                "employee_email": employee.email,
                "auto_send": auto_send,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating employee report: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to generate employee report: {str(e)}"
            )


@cbv(router)
class EmployeeReportDetailResource:
    """
    API Resource for individual employee report details.

    Endpoints:
    - GET: Get full details of a specific employee report
    """

    def get(
        self,
        report_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(require_pm()),
    ):
        """
        Get full details of a specific employee report including content.

        Args:
            report_id: Report ID
            current_user: Authenticated PM user
            session: Database session

        Returns:
            dict: Complete report details including HTML and text content
        """
        try:

            report = session.exec(
                select(EmployeeDailyReport).where(EmployeeDailyReport.id == report_id)
            ).first()

            if not report:
                raise HTTPException(status_code=404, detail="Report not found")

            employee = session.exec(
                select(User).where(User.id == report.employee_id)
            ).first()

            import json

            try:
                achievements = (
                    json.loads(report.achievements) if report.achievements else []
                )
            except:
                achievements = []

            try:
                challenges = json.loads(report.challenges) if report.challenges else []
            except:
                challenges = []

            try:
                recommendations = (
                    json.loads(report.recommendations) if report.recommendations else []
                )
            except:
                recommendations = []

            try:
                focus_areas = (
                    json.loads(report.focus_areas) if report.focus_areas else []
                )
            except:
                focus_areas = []

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
                    "challenges": challenges,
                    "recommendations": recommendations,
                    "focus_areas": focus_areas,
                    "report_body_text": report.report_body_text,
                    "report_body_html": report.report_body_html,
                    "tasks_completed_today": report.tasks_completed_today,
                    "tasks_in_progress": report.tasks_in_progress,
                    "projects_worked_on": report.projects_worked_on,
                    "overall_completion_rate": report.overall_completion_rate,
                    "productivity_score": report.productivity_score,
                    "email_sent": report.email_sent,
                    "email_sent_at": (
                        report.email_sent_at.isoformat()
                        if report.email_sent_at
                        else None
                    ),
                    "recipient_email": report.recipient_email,
                    "email_delivery_status": report.email_delivery_status,
                },
                "employee": {
                    "id": employee.id if employee else None,
                    "name": employee.name if employee else None,
                    "email": employee.email if employee else None,
                    "role": employee.role if employee else None,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching report details: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch report details: {str(e)}"
            )
