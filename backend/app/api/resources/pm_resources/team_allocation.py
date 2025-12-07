"""
API Resources for AI-Powered Team Allocation System
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_session
from app.database.employee_models import User
from app.database.product_manager_models import (
    AllocationPolicy,
    AllocationQuery,
    AllocationRecommendation,
    AllocationRecommendationStatusEnum,
    EmployeeAvailability,
    EmployeeSkill,
    Project,
    ProjectRequirementAnalysis,
)
from app.tasks.requirement_tasks import generate_team_allocation_recommendations
from app.middleware import require_pm
from fastapi import Depends, HTTPException, Query
from fastapi_restful import Resource
from pydantic import BaseModel
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


# Pydantic models for request validation
class TeamAllocationRequest(BaseModel):
    team_size_hint: int = 3
    auto_assign: bool = False
    notify_email: Optional[str] = None


class RecommendationActionRequest(BaseModel):
    action: str  # "approve" or "reject"
    feedback: Optional[str] = None
    reviewer_id: Optional[int] = None


class NaturalLanguageQueryRequest(BaseModel):
    query: str
    queried_by: Optional[int] = None


class SkillAddRequest(BaseModel):
    skill_name: str
    proficiency_level: str = "intermediate"
    years_of_experience: Optional[int] = None
    verified: bool = False


class AvailabilityUpdateRequest(BaseModel):
    current_projects_count: Optional[int] = None
    current_workload_hours_per_week: Optional[float] = None
    max_capacity_hours_per_week: Optional[float] = None
    is_available: Optional[bool] = None
    updated_by: Optional[int] = None


class PolicyCreateRequest(BaseModel):
    policy_name: str
    policy_type: str
    policy_config: Dict[str, Any] = {}
    priority: int = 1
    is_active: bool = True


class TeamAllocationResource(Resource):
    """Generate and manage team allocation recommendations"""

    def post(
        self,
        project_id: int,
        data: TeamAllocationRequest,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """
        Generate AI-powered team allocation recommendations for a project
        
        POST /api/pm/projects/{project_id}/team-allocation
        
        Body:
        {
            "team_size_hint": 3,
            "auto_assign": false,
            "notify_email": "manager@example.com"
        }
        """
        try:
            # Validate project exists
            project = session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Get parameters from Pydantic model
            team_size_hint = data.team_size_hint
            auto_assign = data.auto_assign
            notify_email = data.notify_email

            # Trigger async task
            task = generate_team_allocation_recommendations.delay(
                project_id=project_id,
                team_size_hint=team_size_hint,
                auto_assign=auto_assign,
                notify_email=notify_email,
            )

            return {
                "message": "Team allocation started",
                "task_id": task.id,
                "project_id": project_id,
                "status": "processing",
            }

        except Exception as e:
            logger.error(f"Error starting team allocation: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def get(
        self,
        project_id: int,
        current_user: User = Depends(require_pm),
        status_filter: str = Query(None, alias="status"),
        limit: int = Query(10),
        offset: int = Query(0),
    ):
        """
        Get team allocation recommendations for a project
        
        GET /api/pm/projects/{project_id}/team-allocation?status=pending_review&limit=10
        """
        try:
            session = next(get_session())

            # Build query
            query = select(AllocationRecommendation).where(
                AllocationRecommendation.project_id == project_id
            )

            if status_filter:
                query = query.where(
                    AllocationRecommendation.status == status_filter
                )

            # Order by match score
            query = query.order_by(AllocationRecommendation.match_score.desc())

            # Get total count
            total_count = len(session.exec(query).all())

            # Apply pagination
            recommendations = session.exec(query.offset(offset).limit(limit)).all()

            # Format response
            data = []
            for rec in recommendations:
                employee = session.exec(
                    select(User).where(User.id == rec.employee_id)
                ).first()

                data.append(
                    {
                        "id": rec.id,
                        "employee_id": rec.employee_id,
                        "employee_name": employee.name if employee else "Unknown",
                        "employee_email": employee.email if employee else None,
                        "match_score": rec.match_score,
                        "skill_match_score": rec.skill_match_score,
                        "experience_match_score": rec.experience_match_score,
                        "availability_score": rec.availability_score,
                        "workload_score": rec.workload_score,
                        "status": rec.status.value,
                        "reasoning": rec.reasoning,
                        "matching_skills": json.loads(rec.matching_skills or "[]"),
                        "concerns": json.loads(rec.concerns or "[]"),
                        "policy_violations": json.loads(rec.policy_violations or "[]"),
                        "policy_compliance_score": rec.policy_compliance_score,
                        "proposed_role": rec.proposed_role,
                        "proposed_allocation_percentage": rec.proposed_allocation_percentage,
                        "recommendation_date": rec.recommendation_date.isoformat(),
                        "reviewed_at": (
                            rec.reviewed_at.isoformat() if rec.reviewed_at else None
                        ),
                    }
                )

            return {
                "data": data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            logger.error(f"Error fetching recommendations: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


class RecommendationApprovalResource(Resource):
    """Approve or reject allocation recommendations"""

    def put(
        self,
        recommendation_id: int,
        data: RecommendationActionRequest,
        current_user: User = Depends(require_pm),
    ):
        """
        Approve or reject a recommendation
        
        PUT /api/pm/allocation-recommendations/{recommendation_id}
        
        Body:
        {
            "action": "approve",  // or "reject"
            "feedback": "Great match for this role",
            "reviewer_id": 1
        }
        """
        try:
            session = next(get_session())

            recommendation = session.exec(
                select(AllocationRecommendation).where(
                    AllocationRecommendation.id == recommendation_id
                )
            ).first()

            if not recommendation:
                raise HTTPException(status_code=404, detail="Recommendation not found")

            action = data.action
            feedback = data.feedback
            reviewer_id = data.reviewer_id

            if action == "approve":
                recommendation.status = AllocationRecommendationStatusEnum.APPROVED
                
                # TODO: Actually assign employee to project (create UserProject record)
                from app.database.product_manager_models import UserProject
                
                # Check if already assigned
                existing = session.exec(
                    select(UserProject).where(
                        UserProject.user_id == recommendation.employee_id,
                        UserProject.project_id == recommendation.project_id
                    )
                ).first()
                
                if not existing:
                    user_project = UserProject(
                        user_id=recommendation.employee_id,
                        project_id=recommendation.project_id
                    )
                    session.add(user_project)
                
            elif action == "reject":
                recommendation.status = AllocationRecommendationStatusEnum.REJECTED
            else:
                raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")

            recommendation.feedback_provided = True
            recommendation.feedback_text = feedback
            recommendation.feedback_date = datetime.now()
            recommendation.reviewed_by = reviewer_id
            recommendation.reviewed_at = datetime.now()

            session.add(recommendation)
            session.commit()
            session.refresh(recommendation)

            return {
                "message": f"Recommendation {action}d successfully",
                "recommendation_id": recommendation.id,
                "status": recommendation.status.value,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating recommendation: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


class NaturalLanguageQueryResource(Resource):
    """Natural language interface for team allocation queries"""

    def post(
        self,
        data: NaturalLanguageQueryRequest,
        current_user: User = Depends(require_pm),
    ):
        """
        Process natural language query about team allocation
        
        POST /api/pm/team-allocation/query
        
        Body:
        {
            "query": "Who are the best Python developers available for a new project?",
            "queried_by": 1
        }
        """
        try:
            session = next(get_session())

            query_text = data.query.strip()
            queried_by = data.queried_by

            if not query_text:
                raise HTTPException(status_code=400, detail="Query text is required")

            # Use AI to interpret the query
            from langchain_groq import ChatGroq
            from langchain_core.messages import SystemMessage, HumanMessage
            from app.config import Config

            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=Config.GROQ_API_KEY,
                temperature=0.3,
            )

            system_prompt = """You are a team allocation assistant. Interpret the user's natural language query 
about team allocation and extract:
1. Intent (e.g., find_employees, check_availability, get_skills, recommend_team)
2. Skills mentioned (if any)
3. Project mentioned (if any)
4. Other criteria (experience level, availability, etc.)

Return as JSON:
{
    "intent": "find_employees",
    "skills": ["Python", "FastAPI"],
    "experience_level": "intermediate",
    "availability_required": true,
    "project_name": null
}"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User query: {query_text}"),
            ]

            response = llm.invoke(messages)
            content = response.content

            # Extract JSON
            if isinstance(content, str):
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

            interpreted = json.loads(content) if isinstance(content, str) else content
            intent = interpreted.get("intent", "unknown")
            skills = interpreted.get("skills", [])

            # Execute the query based on intent
            response_data = {}
            response_text = ""

            if intent == "find_employees" and skills:
                # Find employees with matching skills
                matching_employees = []
                
                for skill_name in skills:
                    skill_records = session.exec(
                        select(EmployeeSkill)
                        .where(EmployeeSkill.skill_name.contains(skill_name))
                    ).all()
                    
                    for skill_rec in skill_records:
                        employee = session.exec(
                            select(User).where(User.id == skill_rec.employee_id)
                        ).first()
                        
                        if employee:
                            # Check availability
                            availability = session.exec(
                                select(EmployeeAvailability).where(
                                    EmployeeAvailability.employee_id == employee.id
                                )
                            ).first()
                            
                            matching_employees.append({
                                "id": employee.id,
                                "name": employee.name,
                                "email": employee.email,
                                "skill": skill_rec.skill_name,
                                "proficiency": skill_rec.proficiency_level,
                                "is_available": availability.is_available if availability else True,
                                "current_utilization": (
                                    (availability.current_workload_hours_per_week / 
                                     availability.max_capacity_hours_per_week * 100)
                                    if availability and availability.max_capacity_hours_per_week > 0
                                    else 0
                                ),
                            })
                
                response_data["employees"] = matching_employees[:10]
                response_text = f"Found {len(matching_employees)} employees with skills in {', '.join(skills)}."
                
                if matching_employees:
                    top_3 = matching_employees[:3]
                    response_text += " Top matches:\n"
                    for emp in top_3:
                        response_text += f"- {emp['name']}: {emp['skill']} ({emp['proficiency']}, {emp['current_utilization']:.0f}% utilized)\n"

            elif intent == "check_availability":
                # Get overall availability stats
                availabilities = session.exec(select(EmployeeAvailability)).all()
                
                available_count = sum(1 for a in availabilities if a.is_available)
                avg_utilization = (
                    sum(
                        a.current_workload_hours_per_week / a.max_capacity_hours_per_week * 100
                        for a in availabilities
                        if a.max_capacity_hours_per_week > 0
                    ) / len(availabilities)
                    if availabilities
                    else 0
                )
                
                response_data = {
                    "available_employees": available_count,
                    "total_employees": len(availabilities),
                    "average_utilization": round(avg_utilization, 1),
                }
                
                response_text = (
                    f"{available_count} out of {len(availabilities)} employees are available. "
                    f"Average utilization is {avg_utilization:.1f}%."
                )

            else:
                response_text = "I understand your query, but I need more specific information to help. Try asking about specific skills or employee availability."

            # Save query to database
            query_record = AllocationQuery(
                query_text=query_text,
                queried_by=queried_by,
                interpreted_intent=intent,
                extracted_parameters=json.dumps(interpreted),
                response_text=response_text,
                response_data=json.dumps(response_data),
            )

            session.add(query_record)
            session.commit()

            return {
                "query_id": query_record.id,
                "intent": intent,
                "response": response_text,
                "data": response_data,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing NL query: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


class EmployeeSkillsResource(Resource):
    """Manage employee skills"""

    def get(
        self,
        employee_id: int,
        current_user: User = Depends(require_pm),
    ):
        """Get employee skills"""
        try:
            session = next(get_session())

            skills = session.exec(
                select(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
            ).all()

            data = [
                {
                    "id": s.id,
                    "skill_name": s.skill_name,
                    "proficiency_level": s.proficiency_level,
                    "years_of_experience": s.years_of_experience,
                    "verified": s.verified,
                    "added_at": s.added_at.isoformat(),
                }
                for s in skills
            ]

            return {"data": data}

        except Exception as e:
            logger.error(f"Error fetching skills: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def post(
        self,
        employee_id: int,
        data: SkillAddRequest,
        current_user: User = Depends(require_pm),
    ):
        """Add employee skill"""
        try:
            session = next(get_session())

            skill = EmployeeSkill(
                employee_id=employee_id,
                skill_name=data.skill_name,
                proficiency_level=data.proficiency_level,
                years_of_experience=data.years_of_experience,
                verified=data.verified,
            )

            session.add(skill)
            session.commit()
            session.refresh(skill)

            return {"message": "Skill added", "skill_id": skill.id}

        except Exception as e:
            logger.error(f"Error adding skill: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


class EmployeeAvailabilityResource(Resource):
    """Manage employee availability"""

    def get(
        self,
        employee_id: int,
        current_user: User = Depends(require_pm),
    ):
        """Get employee availability"""
        try:
            session = next(get_session())

            availability = session.exec(
                select(EmployeeAvailability).where(
                    EmployeeAvailability.employee_id == employee_id
                )
            ).first()

            if not availability:
                raise HTTPException(status_code=404, detail="Availability record not found")

            return {
                "employee_id": availability.employee_id,
                "current_projects_count": availability.current_projects_count,
                "current_workload_hours_per_week": availability.current_workload_hours_per_week,
                "max_capacity_hours_per_week": availability.max_capacity_hours_per_week,
                "is_available": availability.is_available,
                "utilization_percentage": (
                    (availability.current_workload_hours_per_week / 
                     availability.max_capacity_hours_per_week * 100)
                    if availability.max_capacity_hours_per_week > 0
                    else 0
                ),
                "last_updated": availability.last_updated.isoformat(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching availability: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def put(
        self,
        employee_id: int,
        data: AvailabilityUpdateRequest,
        current_user: User = Depends(require_pm),
    ):
        """Update employee availability"""
        try:
            session = next(get_session())

            availability = session.exec(
                select(EmployeeAvailability).where(
                    EmployeeAvailability.employee_id == employee_id
                )
            ).first()

            if not availability:
                # Create new record
                availability = EmployeeAvailability(employee_id=employee_id)

            # Update fields from Pydantic model
            if data.current_projects_count is not None:
                availability.current_projects_count = data.current_projects_count
            if data.current_workload_hours_per_week is not None:
                availability.current_workload_hours_per_week = data.current_workload_hours_per_week
            if data.max_capacity_hours_per_week is not None:
                availability.max_capacity_hours_per_week = data.max_capacity_hours_per_week
            if data.is_available is not None:
                availability.is_available = data.is_available

            availability.last_updated = datetime.now()
            availability.updated_by = data.updated_by

            session.add(availability)
            session.commit()

            return {"message": "Availability updated"}

        except Exception as e:
            logger.error(f"Error updating availability: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


class AllocationPolicyResource(Resource):
    """Manage allocation policies"""

    def get(
        self,
        current_user: User = Depends(require_pm),
    ):
        """Get all active policies"""
        try:
            session = next(get_session())

            policies = session.exec(
                select(AllocationPolicy)
                .where(AllocationPolicy.is_active == True)
                .order_by(AllocationPolicy.priority)
            ).all()

            data = [
                {
                    "id": p.id,
                    "policy_name": p.policy_name,
                    "policy_type": p.policy_type.value,
                    "policy_config": json.loads(p.policy_config),
                    "priority": p.priority,
                    "is_active": p.is_active,
                }
                for p in policies
            ]

            return {"data": data}

        except Exception as e:
            logger.error(f"Error fetching policies: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def post(
        self,
        data: PolicyCreateRequest,
        current_user: User = Depends(require_pm),
    ):
        """Create new allocation policy"""
        try:
            session = next(get_session())

            policy = AllocationPolicy(
                policy_name=data.policy_name,
                policy_type=data.policy_type,
                policy_config=json.dumps(data.policy_config),
                priority=data.priority,
                is_active=data.is_active,
            )

            session.add(policy)
            session.commit()
            session.refresh(policy)

            return {"message": "Policy created", "policy_id": policy.id}

        except Exception as e:
            logger.error(f"Error creating policy: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
