from logging import getLogger

from app.database import User, get_session
from app.middleware import require_pm
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session

logger = getLogger(__name__)


class PRDashboardResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """PM Dashboard - View project manager dashboard data"""
        try:
            logger.info(f"Dashboard accessed by: {current_user.email}")

            return {
                "message": "Dashboard data retrieved successfully",
                "user": {
                    "id": current_user.id,
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": current_user.role,
                },
                "projects": [],
                "stats": {
                    "total_projects": 0,
                    "active_projects": 0,
                    "completed_projects": 0,
                },
            }
        except Exception as e:
            logger.error(f"Error in dashboard: {str(e)}", exc_info=True)
            return {
                "message": "Internal server error",
                "error": str(e),
                "status": "error",
            }, 500
