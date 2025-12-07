"""
LangGraph-based AI Agent for generating project roadmaps.

This agent creates comprehensive roadmaps for completing client requirements
using LangChain and LangGraph workflow orchestration.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Annotated, Dict, List, Optional, TypedDict

from app.config import Config
from app.database.product_manager_models import (
    Client,
    Project,
    Requirement,
    RequirementRoadmap,
    StatusTypeEnum,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from sqlmodel import Session, desc, select

logger = logging.getLogger(__name__)


class RoadmapState(TypedDict):
    """State for the roadmap generation workflow."""

    project_id: int
    client_id: int
    project_data: Dict
    client_data: Dict
    requirements: List[Dict]
    categorized_requirements: Dict
    milestones: List[Dict]
    workflow_steps: List[Dict]
    timeline_estimate: Dict
    recommendations: List[str]
    final_roadmap: Dict
    error: Optional[str]


class PMRoadmapAgent:
    """
    AI Agent for generating project roadmaps with milestones and timelines.
    """

    def __init__(self, session: Session):
        self.session = session

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=Config.GROQ_API_KEY,
            max_tokens=4000,
        )

    def generate_roadmap(self, project_id: int) -> Dict:
        """
        Generate a comprehensive project roadmap.

        Args:
            project_id: Project ID to generate roadmap for

        Returns:
            dict: Complete roadmap with milestones and timeline
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
                    "error": "No requirements found",
                    "message": "Cannot generate roadmap without requirements",
                }

            categorized = self._categorize_requirements(requirements)

            milestones = self._generate_milestones_ai(
                project, requirements, categorized
            )

            timeline = self._calculate_timeline(milestones)

            workflow = self._generate_workflow(requirements, categorized)

            recommendations = self._generate_recommendations_ai(
                project, categorized, milestones
            )

            roadmap = {
                "project": {
                    "id": project.id,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "status": project.status,
                },
                "client": {
                    "id": client.id if client else None,
                    "client_id": client.client_id if client else None,
                    "client_name": client.client_name if client else "Unknown",
                    "email": client.email if client else None,
                },
                "generated_at": datetime.utcnow().isoformat(),
                "summary": self._generate_summary(
                    project, requirements, categorized, timeline
                ),
                "categorized_requirements": categorized,
                "milestones": milestones,
                "workflow_steps": workflow,
                "timeline": timeline,
                "recommendations": recommendations,
                "total_requirements": len(requirements),
                "pending_count": len(categorized["pending"]),
                "in_progress_count": len(categorized["in_progress"]),
                "completed_count": len(categorized["completed"]),
            }

            return roadmap

        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _categorize_requirements(self, requirements: List[Requirement]) -> Dict:
        """Categorize requirements by status and priority."""
        pending = []
        in_progress = []
        completed = []

        for req in requirements:
            req_data = {
                "id": req.id,
                "requirement_id": req.requirement_id,
                "description": req.requirements,
                "status": req.status,
                "priority_score": self._calculate_priority(req),
                "complexity": self._estimate_complexity(req),
            }

            if req.status == StatusTypeEnum.PENDING:
                pending.append(req_data)
            elif req.status == StatusTypeEnum.IN_PROGRESS:
                in_progress.append(req_data)
            elif req.status == StatusTypeEnum.COMPLETED:
                completed.append(req_data)

        pending.sort(key=lambda x: x["priority_score"], reverse=True)

        return {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "priority_order": pending + in_progress,
            "complexity_analysis": self._analyze_complexity(
                pending + in_progress + completed
            ),
        }

    def _calculate_priority(self, requirement: Requirement) -> int:
        """Calculate priority score for a requirement."""
        score = 5

        if requirement.status == StatusTypeEnum.IN_PROGRESS:
            score += 5

        desc_lower = requirement.requirements.lower()
        if any(
            word in desc_lower
            for word in ["critical", "urgent", "blocker", "high priority"]
        ):
            score += 3
        if any(
            word in desc_lower
            for word in ["authentication", "security", "payment", "core"]
        ):
            score += 2

        return score

    def _estimate_complexity(self, requirement: Requirement) -> str:
        """Estimate complexity of a requirement."""
        desc = requirement.requirements.lower()
        desc_length = len(requirement.requirements)

        complex_keywords = [
            "integrate",
            "authentication",
            "payment",
            "api",
            "database",
            "migration",
        ]
        medium_keywords = ["update", "modify", "enhance", "improve"]

        if any(word in desc for word in complex_keywords) or desc_length > 100:
            return "high"
        elif any(word in desc for word in medium_keywords) or desc_length > 50:
            return "medium"
        else:
            return "low"

    def _analyze_complexity(self, requirements: List[Dict]) -> Dict:
        """Analyze overall complexity distribution."""
        high = sum(1 for r in requirements if r["complexity"] == "high")
        medium = sum(1 for r in requirements if r["complexity"] == "medium")
        low = sum(1 for r in requirements if r["complexity"] == "low")

        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(requirements),
        }

    def _generate_milestones_ai(
        self, project: Project, requirements: List[Requirement], categorized: Dict
    ) -> List[Dict]:
        """Generate milestones using AI."""
        try:

            req_text = "\n".join(
                [
                    f"- [{r['status']}] {r['requirement_id']}: {r['description']} (Priority: {r['priority_score']}, Complexity: {r['complexity']})"
                    for r in categorized["priority_order"]
                ]
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content="""You are an expert project planner. 
Create logical milestones for this project that group related requirements.
Each milestone should have:
1. A clear, descriptive name
2. A set of related requirements
3. Estimated duration in days
4. Status (PENDING, IN_PROGRESS, or COMPLETED based on requirements)

Create 3-5 meaningful milestones that represent logical phases of the project."""
                    ),
                    HumanMessage(
                        content=f"""
Project: {project.project_name}
Description: {project.description or 'No description'}

Requirements:
{req_text}

Total Requirements: {len(requirements)}
- Pending: {len(categorized['pending'])}
- In Progress: {len(categorized['in_progress'])}
- Completed: {len(categorized['completed'])}

Create 3-5 milestones and assign requirements to each milestone.
Format your response as:
Milestone 1: [Name]
Duration: [X days]
Status: [PENDING/IN_PROGRESS/COMPLETED]
Requirements: [List requirement IDs]
Description: [Brief description]

Milestone 2: ...
"""
                    ),
                ]
            )

            response = self.llm.invoke(prompt.format_messages())
            milestones = self._parse_milestones(response.content, categorized)

            logger.info(f"Generated {len(milestones)} milestones using AI")
            return milestones

        except Exception as e:
            logger.error(f"AI milestone generation failed: {str(e)}, using fallback")
            return self._generate_fallback_milestones(requirements, categorized)

    def _parse_milestones(self, ai_response: str, categorized: Dict) -> List[Dict]:
        """Parse AI response into structured milestones."""
        milestones = []
        current_milestone = None

        lines = ai_response.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("Milestone"):
                if current_milestone:
                    milestones.append(current_milestone)

                parts = line.split(":", 1)
                name = parts[1].strip() if len(parts) > 1 else "Milestone Phase"
                current_milestone = {
                    "name": name,
                    "requirements": [],
                    "estimated_duration_days": 10,
                    "status": "PENDING",
                }
            elif current_milestone:
                if line.lower().startswith("duration:"):
                    try:
                        duration_str = line.split(":")[1].strip()
                        duration = int("".join(filter(str.isdigit, duration_str)))
                        current_milestone["estimated_duration_days"] = duration
                    except:
                        pass
                elif line.lower().startswith("status:"):
                    status = line.split(":")[1].strip().upper()
                    current_milestone["status"] = status

        if current_milestone:
            milestones.append(current_milestone)

        if not milestones:
            return self._generate_fallback_milestones([], categorized)

        all_reqs = (
            categorized["pending"]
            + categorized["in_progress"]
            + categorized["completed"]
        )
        reqs_per_milestone = max(1, len(all_reqs) // len(milestones))

        for i, milestone in enumerate(milestones):
            start_idx = i * reqs_per_milestone
            end_idx = (
                start_idx + reqs_per_milestone
                if i < len(milestones) - 1
                else len(all_reqs)
            )
            milestone["requirements"] = all_reqs[start_idx:end_idx]

            if all(r["status"] == "COMPLETED" for r in milestone["requirements"]):
                milestone["status"] = "COMPLETED"
            elif any(r["status"] == "IN_PROGRESS" for r in milestone["requirements"]):
                milestone["status"] = "IN_PROGRESS"
            else:
                milestone["status"] = "PENDING"

        return milestones

    def _generate_fallback_milestones(
        self, requirements: List[Requirement], categorized: Dict
    ) -> List[Dict]:
        """Generate basic milestones when AI fails."""
        all_reqs = (
            categorized["pending"]
            + categorized["in_progress"]
            + categorized["completed"]
        )

        if not all_reqs:
            return []

        num_milestones = min(4, max(2, len(all_reqs) // 2))
        reqs_per_milestone = max(1, len(all_reqs) // num_milestones)

        milestones = []

        for i in range(num_milestones):
            start_idx = i * reqs_per_milestone
            end_idx = (
                start_idx + reqs_per_milestone
                if i < num_milestones - 1
                else len(all_reqs)
            )
            milestone_reqs = all_reqs[start_idx:end_idx]

            if all(r["status"] == "COMPLETED" for r in milestone_reqs):
                status = "COMPLETED"
            elif any(r["status"] == "IN_PROGRESS" for r in milestone_reqs):
                status = "IN_PROGRESS"
            else:
                status = "PENDING"

            duration = sum(
                (
                    15
                    if r["complexity"] == "high"
                    else 7 if r["complexity"] == "medium" else 3
                )
                for r in milestone_reqs
            )

            milestones.append(
                {
                    "name": f"Phase {i + 1}: Development Sprint",
                    "requirements": milestone_reqs,
                    "estimated_duration_days": duration,
                    "status": status,
                    "description": f"Complete {len(milestone_reqs)} requirements",
                }
            )

        return milestones

    def _calculate_timeline(self, milestones: List[Dict]) -> Dict:
        """Calculate project timeline."""
        start_date = datetime.utcnow()
        total_days = sum(m["estimated_duration_days"] for m in milestones)
        end_date = start_date + timedelta(days=total_days)

        milestones_timeline = []
        current_date = start_date

        for milestone in milestones:
            milestone_end = current_date + timedelta(
                days=milestone["estimated_duration_days"]
            )
            milestones_timeline.append(
                {
                    "milestone": milestone["name"],
                    "start_date": current_date.isoformat(),
                    "end_date": milestone_end.isoformat(),
                    "duration_days": milestone["estimated_duration_days"],
                }
            )
            current_date = milestone_end

        return {
            "start_date": start_date.isoformat(),
            "estimated_completion_date": end_date.isoformat(),
            "total_estimated_days": total_days,
            "milestones_timeline": milestones_timeline,
        }

    def _generate_workflow(
        self, requirements: List[Requirement], categorized: Dict
    ) -> List[Dict]:
        """Generate workflow steps."""
        workflow = []

        if categorized["in_progress"]:
            workflow.append(
                {
                    "step": 1,
                    "name": "Complete In-Progress Work",
                    "requirements": [
                        r["requirement_id"] for r in categorized["in_progress"]
                    ],
                    "priority": "HIGH",
                    "action": "Focus on finishing started work",
                }
            )

        high_priority = [r for r in categorized["pending"] if r["priority_score"] > 7]
        if high_priority:
            workflow.append(
                {
                    "step": len(workflow) + 1,
                    "name": "High Priority Requirements",
                    "requirements": [r["requirement_id"] for r in high_priority],
                    "priority": "HIGH",
                    "action": "Start highest priority pending work",
                }
            )

        remaining = [r for r in categorized["pending"] if r["priority_score"] <= 7]
        if remaining:
            workflow.append(
                {
                    "step": len(workflow) + 1,
                    "name": "Complete Remaining Requirements",
                    "requirements": [r["requirement_id"] for r in remaining],
                    "priority": "MEDIUM",
                    "action": "Complete all remaining work",
                }
            )

        workflow.append(
            {
                "step": len(workflow) + 1,
                "name": "Review & Quality Assurance",
                "requirements": [r["requirement_id"] for r in categorized["completed"]],
                "priority": "MEDIUM",
                "action": "Review and test completed requirements",
            }
        )

        return workflow

    def _generate_recommendations_ai(
        self, project: Project, categorized: Dict, milestones: List[Dict]
    ) -> List[str]:
        """Generate AI-powered recommendations."""
        recommendations = []

        if len(categorized["in_progress"]) > 3:
            recommendations.append(
                "⚠️ Focus: Too many concurrent tasks. Complete in-progress work first."
            )

        if len(categorized["pending"]) > 10:
            recommendations.append(
                "📋 Planning: Large backlog detected. Consider breaking down complex requirements."
            )

        complexity = categorized["complexity_analysis"]
        if complexity["high"] > complexity["low"] + complexity["medium"]:
            recommendations.append(
                "🎯 Risk: Many high-complexity requirements. Consider additional resources or timeline adjustment."
            )

        return recommendations

    def _generate_summary(
        self,
        project: Project,
        requirements: List[Requirement],
        categorized: Dict,
        timeline: Dict,
    ) -> str:
        """Generate roadmap summary."""
        return f"""Project roadmap for {project.project_name} includes {len(requirements)} requirements 
organized into {len(timeline.get('milestones_timeline', []))} milestones. Currently {len(categorized['completed'])} requirements completed, {len(categorized['pending'])} pending. 
Estimated completion: {timeline['total_estimated_days']} days."""

    def save_roadmap(
        self,
        roadmap: Dict,
        client_id: int,
        trigger_type: str = "manual",
        generated_by: Optional[int] = None,
    ) -> RequirementRoadmap:
        """
        Save generated roadmap to database.

        Args:
            roadmap: Generated roadmap dictionary
            client_id: Client ID
            trigger_type: What triggered the generation
            generated_by: Optional user ID who generated the roadmap

        Returns:
            RequirementRoadmap: Saved roadmap database object
        """
        try:
            project_id = roadmap["project"]["id"]

            existing_roadmaps = self.session.exec(
                select(RequirementRoadmap).where(
                    RequirementRoadmap.project_id == project_id,
                    RequirementRoadmap.client_id == client_id,
                    RequirementRoadmap.is_current == True,
                )
            ).all()

            for existing in existing_roadmaps:
                existing.is_current = False
                self.session.add(existing)

            latest = self.session.exec(
                select(RequirementRoadmap)
                .where(
                    RequirementRoadmap.project_id == project_id,
                    RequirementRoadmap.client_id == client_id,
                )
                .order_by(desc(RequirementRoadmap.version))
            ).first()

            next_version = (latest.version + 1) if latest else 1

            new_roadmap = RequirementRoadmap(
                project_id=project_id,
                client_id=client_id,
                roadmap_data=json.dumps(roadmap),
                summary=roadmap.get("summary"),
                estimated_completion_days=roadmap.get("timeline", {}).get(
                    "total_estimated_days"
                ),
                trigger_type=trigger_type,
                is_current=True,
                version=next_version,
                generated_by=generated_by,
            )

            self.session.add(new_roadmap)
            self.session.commit()
            self.session.refresh(new_roadmap)

            logger.info(f"Roadmap saved successfully - version {next_version}")
            return new_roadmap

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving roadmap: {str(e)}", exc_info=True)
            raise


def get_pm_roadmap_agent(session: Session) -> PMRoadmapAgent:
    """Factory function to create PM roadmap agent."""
    return PMRoadmapAgent(session)
