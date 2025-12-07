from logging import getLogger
from typing import Optional

from app.database import User, get_session
from app.middleware import require_pm
from app.tasks.requirement_tasks import analyze_project_requirements_ai
from app.core.agents.pm_agents.pm_requirements_agent import get_pm_requirements_agent
from fastapi import Depends, HTTPException, Query
from fastapi_restful import Resource
from pydantic import BaseModel
from sqlmodel import Session

logger = getLogger(__name__)


class AnalysisTriggerRequest(BaseModel):
    """Request model for triggering analysis."""
    notify_email: Optional[str] = None
    send_email: bool = True


class RequirementAnalysisResource(Resource):
    """
    API Resource for AI-powered requirement analysis.
    
    Endpoints:
    - POST: Trigger async AI analysis (with optional email)
    - GET: Get immediate sync AI analysis (for frontend display)
    """
    
    def get(
        self,
        project_id: int,
        format: str = Query("json", description="Response format: json or html"),
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Get immediate AI-powered requirement analysis.
        
        This is a synchronous endpoint that returns analysis instantly
        for display in the frontend.
        
        Args:
            project_id: Project ID to analyze
            format: Response format (json or html)
            current_user: Authenticated PM user
            session: Database session
            
        Returns:
            dict: AI-generated analysis report
        """
        try:
            logger.info(
                f"Synchronous AI analysis requested for project {project_id} by {current_user.email}"
            )
            
            # Get AI agent
            agent = get_pm_requirements_agent(session)
            
            # Run analysis
            report = agent.analyze(project_id)
            
            if "error" in report:
                raise HTTPException(status_code=404, detail=report["error"])
            
            # If HTML format requested, generate HTML
            if format.lower() == "html":
                from app.tasks.requirement_tasks import _generate_html_report
                html = _generate_html_report(report)
                return {
                    "message": "AI Analysis completed successfully",
                    "format": "html",
                    "html": html,
                    "data": report,
                }
            
            return {
                "message": "AI Analysis completed successfully",
                "format": "json",
                "data": report,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"AI Analysis error: {str(e)}")
    
    def post(
        self,
        project_id: int,
        request_data: AnalysisTriggerRequest = None,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Trigger async AI-powered requirement analysis.
        
        This triggers a background Celery task that will:
        1. Analyze project requirements using AI
        2. Generate comprehensive report
        3. Optionally send email to specified address
        
        Args:
            project_id: Project ID to analyze
            request_data: Optional request body with email settings
            current_user: Authenticated PM user
            session: Database session
            
        Returns:
            dict: Task information
        """
        try:
            logger.info(
                f"Async AI analysis triggered for project {project_id} by {current_user.email}"
            )
            
            # Determine email settings
            send_email = request_data.send_email if request_data else True
            notify_email = (
                request_data.notify_email if request_data and request_data.notify_email
                else current_user.email
            ) if send_email else None
            
            # Trigger async AI analysis
            task = analyze_project_requirements_ai.delay(
                project_id=project_id,
                notify_email=notify_email
            )
            
            message = "AI Analysis started."
            if notify_email:
                message += f" Report will be sent to {notify_email}."
            
            return {
                "message": message,
                "data": {
                    "task_id": task.id,
                    "project_id": project_id,
                    "notify_email": notify_email,
                    "status": "processing",
                },
            }
            
        except Exception as e:
            logger.error(f"Error triggering AI analysis: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to trigger AI analysis")
