import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.database import get_session
from app.database.product_manager_models import (
    Requirement,
    Project,
    Client,
    StatusTypeEnum,
)
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class RequirementAnalysisAgent:
    """
    AI Agent for analyzing project requirements and generating execution recommendations.

    This agent:
    1. Fetches all requirements for a project
    2. Analyzes requirement status and complexity
    3. Generates execution plan and recommendations
    4. Provides priority ordering and risk assessment
    """

    def __init__(self, session: Session):
        self.session = session

    def analyze_project_requirements(
        self, project_id: int, new_requirement_id: Optional[int] = None
    ) -> Dict:
        """
        Analyze all requirements for a project and generate execution plan.

        Args:
            project_id: Project ID to analyze
            new_requirement_id: ID of newly added requirement (optional)

        Returns:
            dict: Analysis report with recommendations
        """
        try:

            project = self.session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                return {"error": "Project not found"}

            client = self.session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            requirements = self.session.exec(
                select(Requirement).where(Requirement.project_id == project_id)
            ).all()

            if not requirements:
                return {
                    "status": "no_requirements",
                    "message": "No requirements found for this project",
                }

            analysis = self._analyze_requirements(requirements, new_requirement_id)

            execution_plan = self._generate_execution_plan(requirements, analysis)

            recommendations = self._generate_recommendations(
                requirements, analysis, project
            )

            report = {
                "project": {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "status": project.status,
                },
                "client": {
                    "name": client.client_name if client else "Unknown",
                    "email": client.email if client else None,
                },
                "analysis_date": datetime.utcnow().isoformat(),
                "summary": analysis,
                "execution_plan": execution_plan,
                "recommendations": recommendations,
                "requirements_details": self._format_requirements(requirements),
            }

            return report

        except Exception as e:
            logger.error(f"Error analyzing requirements: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _analyze_requirements(
        self, requirements: List[Requirement], new_requirement_id: Optional[int]
    ) -> Dict:
        """Analyze requirement statistics and patterns."""
        total = len(requirements)
        pending = sum(1 for r in requirements if r.status == StatusTypeEnum.PENDING)
        in_progress = sum(
            1 for r in requirements if r.status == StatusTypeEnum.IN_PROGRESS
        )
        completed = sum(1 for r in requirements if r.status == StatusTypeEnum.COMPLETED)

        completion_rate = (completed / total * 100) if total > 0 else 0

        new_requirement = None
        if new_requirement_id:
            new_requirement = next(
                (r for r in requirements if r.id == new_requirement_id), None
            )

        return {
            "total_requirements": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "completion_rate": round(completion_rate, 2),
            "new_requirement": (
                {
                    "id": new_requirement.requirement_id if new_requirement else None,
                    "description": (
                        new_requirement.requirements if new_requirement else None
                    ),
                }
                if new_requirement
                else None
            ),
        }

    def _generate_execution_plan(
        self, requirements: List[Requirement], analysis: Dict
    ) -> List[Dict]:
        """Generate prioritized execution plan."""
        plan = []

        in_progress_reqs = [
            r for r in requirements if r.status == StatusTypeEnum.IN_PROGRESS
        ]
        if in_progress_reqs:
            plan.append(
                {
                    "phase": "1. Complete In-Progress Tasks",
                    "priority": "HIGH",
                    "requirements": [
                        {
                            "requirement_id": r.requirement_id,
                            "description": r.requirements,
                            "status": r.status,
                        }
                        for r in in_progress_reqs
                    ],
                    "rationale": "Complete ongoing work to maintain momentum and avoid context switching.",
                }
            )

        pending_reqs = [r for r in requirements if r.status == StatusTypeEnum.PENDING]
        if pending_reqs:
            plan.append(
                {
                    "phase": "2. Start Pending Requirements",
                    "priority": "MEDIUM",
                    "requirements": [
                        {
                            "requirement_id": r.requirement_id,
                            "description": r.requirements,
                            "status": r.status,
                        }
                        for r in pending_reqs
                    ],
                    "rationale": "Begin work on pending requirements in order of business value.",
                }
            )

        completed_reqs = [
            r for r in requirements if r.status == StatusTypeEnum.COMPLETED
        ]
        if completed_reqs:
            plan.append(
                {
                    "phase": "3. Review & Validate Completed Items",
                    "priority": "LOW",
                    "requirements": [
                        {
                            "requirement_id": r.requirement_id,
                            "description": r.requirements,
                            "status": r.status,
                        }
                        for r in completed_reqs
                    ],
                    "rationale": "Ensure quality and completeness of finished requirements.",
                }
            )

        return plan

    def _generate_recommendations(
        self, requirements: List[Requirement], analysis: Dict, project: Project
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if analysis["in_progress"] > 3:
            recommendations.append(
                "⚠️ HIGH WORKLOAD: You have more than 3 requirements in progress. "
                "Consider focusing on completing existing tasks before starting new ones."
            )

        if analysis["pending"] > 5:
            recommendations.append(
                "📋 BACKLOG ALERT: Large number of pending requirements detected. "
                "Prioritize and break down complex requirements into smaller tasks."
            )

        if analysis["completion_rate"] < 30 and analysis["total_requirements"] > 5:
            recommendations.append(
                "📊 LOW COMPLETION RATE: Less than 30% of requirements completed. "
                "Review project timeline and resource allocation."
            )
        elif analysis["completion_rate"] > 70:
            recommendations.append(
                "✅ GOOD PROGRESS: Over 70% completion rate. Keep up the momentum!"
            )

        if analysis["new_requirement"]:
            recommendations.append(
                f"🆕 NEW REQUIREMENT ADDED: '{analysis['new_requirement']['description']}'. "
                "Review impact on existing timeline and dependencies."
            )

        if project.status == StatusTypeEnum.PENDING and analysis["in_progress"] == 0:
            recommendations.append(
                "🚀 PROJECT START: No active work detected. Begin with highest priority requirements."
            )

        if (
            project.status == StatusTypeEnum.IN_PROGRESS
            and analysis["pending"] == 0
            and analysis["in_progress"] == 0
        ):
            recommendations.append(
                "🎯 NEAR COMPLETION: All requirements completed or in final stages. "
                "Consider project closure procedures."
            )

        recommendations.append(
            "💡 TIP: Regular status updates and daily standups help track progress effectively."
        )

        return recommendations

    def _format_requirements(self, requirements: List[Requirement]) -> List[Dict]:
        """Format requirements for report."""
        return [
            {
                "requirement_id": r.requirement_id,
                "description": r.requirements,
                "status": r.status,
                "client_id": r.client_id,
            }
            for r in requirements
        ]


def get_requirement_agent(session: Session) -> RequirementAnalysisAgent:
    """Get requirement analysis agent instance."""
    return RequirementAnalysisAgent(session)
