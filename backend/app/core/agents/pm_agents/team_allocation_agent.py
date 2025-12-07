"""
AI-Powered Team Allocation Agent using LangGraph

This agent analyzes project requirements and recommends optimal employee allocations
based on skills, experience, availability, and company policies.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, TypedDict

from app.config import Config
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class TeamAllocationState(TypedDict):
    """State for the team allocation workflow"""

    # Input
    project_id: int
    project_description: str
    team_size_hint: int
    required_skills_hint: List[str]
    auto_assign: bool

    # Project analysis
    required_skills: List[Dict[str, Any]]
    required_roles: List[str]
    complexity_score: float
    estimated_duration_weeks: int
    experience_level_needed: Dict[str, Any]

    # Employee data
    available_employees: List[Dict[str, Any]]
    employee_skills: Dict[int, List[Dict[str, Any]]]
    employee_availability: Dict[int, Dict[str, Any]]

    # Allocation policies
    active_policies: List[Dict[str, Any]]
    policy_constraints: Dict[str, Any]

    # Recommendations
    recommendations: List[Dict[str, Any]]
    ranked_candidates: List[Dict[str, Any]]

    # Results
    final_recommendations: List[Dict[str, Any]]
    reasoning: str
    success: bool
    error: str


class TeamAllocationAgent:
    """AI agent for analyzing projects and recommending team allocations"""

    def __init__(self, session: Session = None):
        self.session = session
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=Config.GROQ_API_KEY,
            temperature=0.3,
        )
        self.graph = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for team allocation"""

        workflow = StateGraph(TeamAllocationState)

        # Define nodes
        workflow.add_node("analyze_project", self.analyze_project_requirements)
        workflow.add_node("fetch_employees", self.fetch_available_employees)
        workflow.add_node("fetch_policies", self.fetch_allocation_policies)
        workflow.add_node("score_candidates", self.score_employee_candidates)
        workflow.add_node("apply_policies", self.apply_policy_constraints)
        workflow.add_node("rank_recommendations", self.rank_and_select_recommendations)
        workflow.add_node("generate_reasoning", self.generate_explainable_reasoning)

        # Define edges
        workflow.set_entry_point("analyze_project")
        workflow.add_edge("analyze_project", "fetch_employees")
        workflow.add_edge("fetch_employees", "fetch_policies")
        workflow.add_edge("fetch_policies", "score_candidates")
        workflow.add_edge("score_candidates", "apply_policies")
        workflow.add_edge("apply_policies", "rank_recommendations")
        workflow.add_edge("rank_recommendations", "generate_reasoning")
        workflow.add_edge("generate_reasoning", END)

        return workflow.compile()

    def analyze_project_requirements(self, state: TeamAllocationState) -> Dict:
        """Node 1: Analyze project description to extract requirements"""
        logger.info(
            f"Analyzing project requirements for project_id: {state['project_id']}"
        )

        try:
            # Get project from database
            from app.database.product_manager_models import Project

            project = self.session.exec(
                select(Project).where(Project.id == state["project_id"])
            ).first()

            if not project:
                return {
                    "success": False,
                    "error": f"Project {state['project_id']} not found",
                }

            project_description = project.description or state.get(
                "project_description", ""
            )

            # Use AI to analyze project requirements
            system_prompt = """You are an expert project analyst. Analyze the project description and extract:
1. Required technical skills with proficiency levels (beginner/intermediate/advanced/expert)
2. Required roles (e.g., frontend dev, backend dev, QA, DevOps, UI/UX)
3. Project complexity score (0-100)
4. Estimated duration in weeks
5. Minimum and preferred experience levels

Return your analysis as JSON with this structure:
{
    "required_skills": [
        {"skill": "Python", "proficiency": "advanced", "importance": "critical"},
        {"skill": "React", "proficiency": "intermediate", "importance": "high"}
    ],
    "required_roles": ["backend_developer", "frontend_developer", "qa_engineer"],
    "complexity_score": 75,
    "estimated_duration_weeks": 12,
    "experience_level_needed": {
        "minimum_years": 2,
        "preferred_years": 4,
        "senior_required": true
    },
    "estimated_team_size": 4
}"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"""Project: {project.project_name}
Description: {project_description}

Additional hints:
- Team size hint: {state.get('team_size_hint', 'Not specified')}
- Required skills hint: {state.get('required_skills_hint', 'Not specified')}

Analyze this project and extract requirements."""
                ),
            ]

            response = self.llm.invoke(messages)
            content = response.content

            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            # Update state
            state["required_skills"] = analysis.get("required_skills", [])
            state["required_roles"] = analysis.get("required_roles", [])
            state["complexity_score"] = analysis.get("complexity_score", 50)
            state["estimated_duration_weeks"] = analysis.get(
                "estimated_duration_weeks", 8
            )
            state["experience_level_needed"] = analysis.get(
                "experience_level_needed", {}
            )

            # Save analysis to database
            from app.database.product_manager_models import ProjectRequirementAnalysis

            analysis_record = ProjectRequirementAnalysis(
                project_id=state["project_id"],
                required_skills=json.dumps(analysis.get("required_skills", [])),
                experience_level_needed=json.dumps(
                    analysis.get("experience_level_needed", {})
                ),
                estimated_team_size=analysis.get("estimated_team_size", 3),
                estimated_duration_weeks=analysis.get("estimated_duration_weeks", 8),
                complexity_score=analysis.get("complexity_score", 50),
                recommended_roles=json.dumps(analysis.get("required_roles", [])),
                analysis_confidence=0.85,
                raw_analysis_text=str(response.content),
            )

            self.session.add(analysis_record)
            self.session.commit()

            logger.info("Project analysis completed successfully")
            return state

        except Exception as e:
            logger.error(f"Error analyzing project: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def fetch_available_employees(self, state: TeamAllocationState) -> Dict:
        """Node 2: Fetch available employees with their skills"""
        logger.info("Fetching available employees")

        try:
            from app.database.employee_models import RoleEnum, User
            from app.database.product_manager_models import (
                EmployeeAvailability,
                EmployeeSkill,
            )

            # Fetch all employees (excluding managers and HR)
            employees = self.session.exec(
                select(User).where(User.role == RoleEnum.EMPLOYEE)
            ).all()

            available_employees = []
            employee_skills = {}
            employee_availability = {}

            for emp in employees:
                # Get skills
                skills = self.session.exec(
                    select(EmployeeSkill).where(EmployeeSkill.employee_id == emp.id)
                ).all()

                employee_skills[emp.id] = [
                    {
                        "skill": s.skill_name,
                        "proficiency": s.proficiency_level,
                        "years": s.years_of_experience or 0,
                        "verified": s.verified,
                    }
                    for s in skills
                ]

                # Get availability
                availability = self.session.exec(
                    select(EmployeeAvailability).where(
                        EmployeeAvailability.employee_id == emp.id
                    )
                ).first()

                if availability:
                    employee_availability[emp.id] = {
                        "is_available": availability.is_available,
                        "current_projects": availability.current_projects_count,
                        "current_workload": availability.current_workload_hours_per_week,
                        "max_capacity": availability.max_capacity_hours_per_week,
                        "utilization": (
                            (
                                availability.current_workload_hours_per_week
                                / availability.max_capacity_hours_per_week
                            )
                            * 100
                            if availability.max_capacity_hours_per_week > 0
                            else 0
                        ),
                    }
                else:
                    # Default availability if not set
                    employee_availability[emp.id] = {
                        "is_available": True,
                        "current_projects": 0,
                        "current_workload": 0,
                        "max_capacity": 40,
                        "utilization": 0,
                    }

                available_employees.append(
                    {
                        "id": emp.id,
                        "name": emp.name,
                        "email": emp.email,
                        "department_id": emp.department_id,
                    }
                )

            state["available_employees"] = available_employees
            state["employee_skills"] = employee_skills
            state["employee_availability"] = employee_availability

            logger.info(f"Fetched {len(available_employees)} available employees")
            return state

        except Exception as e:
            logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def fetch_allocation_policies(self, state: TeamAllocationState) -> Dict:
        """Node 3: Fetch active allocation policies"""
        logger.info("Fetching allocation policies")

        try:
            from app.database.product_manager_models import AllocationPolicy

            policies = self.session.exec(
                select(AllocationPolicy)
                .where(AllocationPolicy.is_active == True)
                .order_by(AllocationPolicy.priority.desc())
            ).all()

            active_policies = []
            policy_constraints = {}

            for policy in policies:
                config = json.loads(policy.policy_config)
                active_policies.append(
                    {
                        "name": policy.policy_name,
                        "type": policy.policy_type.value,
                        "config": config,
                        "priority": policy.priority,
                    }
                )

                # Store constraints for easy access
                if policy.policy_type.value not in policy_constraints:
                    policy_constraints[policy.policy_type.value] = []
                policy_constraints[policy.policy_type.value].append(config)

            state["active_policies"] = active_policies
            state["policy_constraints"] = policy_constraints

            logger.info(f"Loaded {len(active_policies)} active policies")
            return state

        except Exception as e:
            logger.error(f"Error fetching policies: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def score_employee_candidates(self, state: TeamAllocationState) -> Dict:
        """Node 4: Score each employee based on project fit"""
        logger.info("Scoring employee candidates")

        try:
            required_skills = state.get("required_skills", [])
            available_employees = state.get("available_employees", [])
            employee_skills = state.get("employee_skills", {})
            employee_availability = state.get("employee_availability", {})

            ranked_candidates = []

            for emp in available_employees:
                emp_id = emp["id"]
                emp_skills_list = employee_skills.get(emp_id, [])
                emp_avail = employee_availability.get(emp_id, {})

                # Calculate skill match score
                skill_match_score = self._calculate_skill_match(
                    required_skills, emp_skills_list
                )

                # Calculate availability score
                availability_score = self._calculate_availability_score(emp_avail)

                # Calculate experience match score
                experience_match_score = self._calculate_experience_match(
                    state.get("experience_level_needed", {}), emp_skills_list
                )

                # Calculate workload score (inverse of current utilization)
                workload_score = 100 - emp_avail.get("utilization", 0)

                # Overall match score (weighted average)
                match_score = (
                    skill_match_score * 0.40
                    + experience_match_score * 0.25
                    + availability_score * 0.20
                    + workload_score * 0.15
                )

                candidate = {
                    "employee_id": emp_id,
                    "employee_name": emp["name"],
                    "match_score": round(match_score, 2),
                    "skill_match_score": round(skill_match_score, 2),
                    "experience_match_score": round(experience_match_score, 2),
                    "availability_score": round(availability_score, 2),
                    "workload_score": round(workload_score, 2),
                    "matching_skills": self._get_matching_skills(
                        required_skills, emp_skills_list
                    ),
                    "current_utilization": emp_avail.get("utilization", 0),
                }

                ranked_candidates.append(candidate)

            # Sort by match score
            ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)

            state["ranked_candidates"] = ranked_candidates
            logger.info(f"Scored {len(ranked_candidates)} candidates")
            return state

        except Exception as e:
            logger.error(f"Error scoring candidates: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _calculate_skill_match(
        self, required_skills: List[Dict], employee_skills: List[Dict]
    ) -> float:
        """Calculate how well employee skills match project requirements"""
        if not required_skills:
            return 50.0

        proficiency_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}

        total_score = 0
        max_possible_score = 0

        for req_skill in required_skills:
            req_skill_name = req_skill.get("skill", "").lower()
            req_proficiency = req_skill.get("proficiency", "intermediate").lower()
            importance = req_skill.get("importance", "medium")

            # Importance weighting
            importance_weight = {"critical": 3, "high": 2, "medium": 1, "low": 0.5}.get(
                importance, 1
            )

            max_possible_score += 4 * importance_weight

            # Find matching skill in employee profile
            for emp_skill in employee_skills:
                emp_skill_name = emp_skill.get("skill", "").lower()
                if req_skill_name in emp_skill_name or emp_skill_name in req_skill_name:
                    emp_proficiency = emp_skill.get("proficiency", "beginner").lower()
                    req_level = proficiency_map.get(req_proficiency, 2)
                    emp_level = proficiency_map.get(emp_proficiency, 1)

                    # Score based on proficiency match
                    if emp_level >= req_level:
                        total_score += 4 * importance_weight
                    elif emp_level == req_level - 1:
                        total_score += 2 * importance_weight
                    else:
                        total_score += 1 * importance_weight
                    break

        if max_possible_score == 0:
            return 50.0

        return (total_score / max_possible_score) * 100

    def _calculate_availability_score(self, availability: Dict) -> float:
        """Calculate availability score"""
        if not availability.get("is_available", True):
            return 0.0

        utilization = availability.get("utilization", 0)
        if utilization >= 100:
            return 0.0
        elif utilization >= 80:
            return 25.0
        elif utilization >= 60:
            return 50.0
        elif utilization >= 40:
            return 75.0
        else:
            return 100.0

    def _calculate_experience_match(
        self, required_exp: Dict, employee_skills: List[Dict]
    ) -> float:
        """Calculate experience level match"""
        if not required_exp or not employee_skills:
            return 50.0

        # Calculate average years of experience
        total_years = sum(s.get("years", 0) for s in employee_skills)
        avg_years = total_years / len(employee_skills) if employee_skills else 0

        min_years = required_exp.get("minimum_years", 0)
        preferred_years = required_exp.get("preferred_years", 3)

        if avg_years >= preferred_years:
            return 100.0
        elif avg_years >= min_years:
            return 70.0
        else:
            return max(30.0, (avg_years / min_years) * 50)

    def _get_matching_skills(
        self, required_skills: List[Dict], employee_skills: List[Dict]
    ) -> List[str]:
        """Get list of matching skills"""
        matching = []
        for req in required_skills:
            req_name = req.get("skill", "").lower()
            for emp in employee_skills:
                emp_name = emp.get("skill", "").lower()
                if req_name in emp_name or emp_name in req_name:
                    matching.append(emp.get("skill"))
                    break
        return matching

    def apply_policy_constraints(self, state: TeamAllocationState) -> Dict:
        """Node 5: Apply company policies to filter/adjust recommendations"""
        logger.info("Applying policy constraints")

        try:
            ranked_candidates = state.get("ranked_candidates", [])
            policy_constraints = state.get("policy_constraints", {})
            employee_availability = state.get("employee_availability", {})

            filtered_candidates = []

            for candidate in ranked_candidates:
                emp_id = candidate["employee_id"]
                emp_avail = employee_availability.get(emp_id, {})

                violations = []
                compliance_score = 100.0

                # Check max projects per employee policy
                max_projects_policies = policy_constraints.get(
                    "max_projects_per_employee", []
                )
                for policy in max_projects_policies:
                    max_projects = policy.get("max_projects", 5)
                    if emp_avail.get("current_projects", 0) >= max_projects:
                        violations.append(
                            f"Exceeds max projects limit ({max_projects})"
                        )
                        compliance_score -= 50

                # Check max workload hours policy
                max_workload_policies = policy_constraints.get("max_workload_hours", [])
                for policy in max_workload_policies:
                    max_hours = policy.get("max_hours_per_week", 40)
                    if emp_avail.get("current_workload", 0) >= max_hours:
                        violations.append(f"Exceeds max workload ({max_hours}h/week)")
                        compliance_score -= 30

                candidate["policy_violations"] = violations
                candidate["policy_compliance_score"] = max(0, compliance_score)

                # Only include candidates with reasonable compliance
                if compliance_score >= 30:
                    filtered_candidates.append(candidate)

            state["ranked_candidates"] = filtered_candidates
            logger.info(
                f"After policy filtering: {len(filtered_candidates)} candidates remain"
            )
            return state

        except Exception as e:
            logger.error(f"Error applying policies: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def rank_and_select_recommendations(self, state: TeamAllocationState) -> Dict:
        """Node 6: Select top recommendations for the team"""
        logger.info("Ranking and selecting final recommendations")

        try:
            ranked_candidates = state.get("ranked_candidates", [])
            team_size_hint = state.get("team_size_hint", 3)
            required_roles = state.get("required_roles", [])

            # Adjust final scores based on policy compliance
            for candidate in ranked_candidates:
                policy_score = candidate.get("policy_compliance_score", 100)
                original_score = candidate.get("match_score", 0)
                # Adjust match score by policy compliance
                candidate["final_score"] = (original_score * 0.7) + (policy_score * 0.3)

            # Re-sort by final score
            ranked_candidates.sort(key=lambda x: x["final_score"], reverse=True)

            # Select top N candidates
            num_to_recommend = min(len(ranked_candidates), max(team_size_hint, 5))
            final_recommendations = ranked_candidates[:num_to_recommend]

            state["final_recommendations"] = final_recommendations
            state["recommendations"] = final_recommendations  # For compatibility

            logger.info(f"Selected {len(final_recommendations)} final recommendations")
            return state

        except Exception as e:
            logger.error(f"Error ranking recommendations: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def generate_explainable_reasoning(self, state: TeamAllocationState) -> Dict:
        """Node 7: Generate human-readable explanations for recommendations"""
        logger.info("Generating explainable reasoning")

        try:
            final_recommendations = state.get("final_recommendations", [])
            required_skills = state.get("required_skills", [])
            required_roles = state.get("required_roles", [])

            # Use AI to generate natural language explanation
            system_prompt = """You are an AI team allocation assistant. Generate a clear, 
concise explanation for why these employees were recommended for the project.

Focus on:
1. How their skills match project requirements
2. Their availability and current workload
3. Any policy considerations
4. Overall team composition balance

Keep the explanation professional and actionable."""

            rec_summary = "\n".join(
                [
                    f"- {r['employee_name']}: Match Score {r['final_score']:.1f}%, "
                    f"Skills: {', '.join(r['matching_skills'][:3])}, "
                    f"Utilization: {r['current_utilization']:.0f}%"
                    for r in final_recommendations[:5]
                ]
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"""Project Requirements:
- Required Skills: {', '.join([s['skill'] for s in required_skills])}
- Required Roles: {', '.join(required_roles)}

Recommended Employees:
{rec_summary}

Provide a brief explanation for these recommendations."""
                ),
            ]

            response = self.llm.invoke(messages)
            reasoning = response.content.strip()

            state["reasoning"] = reasoning
            state["success"] = True

            logger.info("Generated explainable reasoning")
            return state

        except Exception as e:
            logger.error(f"Error generating reasoning: {str(e)}", exc_info=True)
            # Don't fail the whole process if reasoning generation fails
            state["reasoning"] = (
                "Recommendations generated based on skill matching and availability."
            )
            state["success"] = True
            return state

    def generate_recommendations(
        self,
        project_id: int,
        team_size_hint: int = 3,
        required_skills_hint: List[str] = None,
        auto_assign: bool = False,
    ) -> Dict[str, Any]:
        """
        Main entry point: Generate team allocation recommendations for a project
        """
        try:
            initial_state = {
                "project_id": project_id,
                "project_description": "",
                "team_size_hint": team_size_hint,
                "required_skills_hint": required_skills_hint or [],
                "auto_assign": auto_assign,
                "required_skills": [],
                "required_roles": [],
                "complexity_score": 0,
                "estimated_duration_weeks": 0,
                "experience_level_needed": {},
                "available_employees": [],
                "employee_skills": {},
                "employee_availability": {},
                "active_policies": [],
                "policy_constraints": {},
                "recommendations": [],
                "ranked_candidates": [],
                "final_recommendations": [],
                "reasoning": "",
                "success": False,
                "error": "",
            }

            final_state = self.graph.invoke(initial_state)

            if not final_state.get("success"):
                return {
                    "success": False,
                    "error": final_state.get("error", "Unknown error occurred"),
                }

            # Save recommendations to database
            from app.database.product_manager_models import AllocationRecommendation

            recommendations_saved = []
            for rec in final_state.get("final_recommendations", []):
                db_rec = AllocationRecommendation(
                    project_id=project_id,
                    employee_id=rec["employee_id"],
                    match_score=rec.get("final_score", 0),
                    skill_match_score=rec.get("skill_match_score", 0),
                    experience_match_score=rec.get("experience_match_score", 0),
                    availability_score=rec.get("availability_score", 0),
                    workload_score=rec.get("workload_score", 0),
                    reasoning=f"Match Score: {rec.get('final_score', 0):.1f}%. "
                    f"Matching Skills: {', '.join(rec.get('matching_skills', []))}",
                    matching_skills=json.dumps(rec.get("matching_skills", [])),
                    concerns=json.dumps(rec.get("policy_violations", [])),
                    policy_violations=json.dumps(rec.get("policy_violations", [])),
                    policy_compliance_score=rec.get("policy_compliance_score", 100),
                    status="auto_assigned" if auto_assign else "pending_review",
                )

                self.session.add(db_rec)
                recommendations_saved.append(
                    {
                        "employee_id": rec["employee_id"],
                        "employee_name": rec["employee_name"],
                        "match_score": rec.get("final_score", 0),
                        "reasoning": db_rec.reasoning,
                    }
                )

            self.session.commit()

            return {
                "success": True,
                "recommendations": recommendations_saved,
                "reasoning": final_state.get("reasoning", ""),
                "total_candidates_analyzed": len(
                    final_state.get("available_employees", [])
                ),
                "recommendations_count": len(recommendations_saved),
            }

        except Exception as e:
            logger.error(f"Error in team allocation: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
