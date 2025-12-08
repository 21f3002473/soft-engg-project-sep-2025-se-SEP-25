import logging
from datetime import datetime
from typing import Annotated, Dict, List, Optional, TypedDict

from app.config import Config
from app.database.product_manager_models import (
    Client,
    Project,
    Requirement,
    StatusTypeEnum,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class RequirementAnalysisState(TypedDict):
    """State for the requirement analysis agent."""

    project_id: int
    new_requirement_id: Optional[int]
    project_data: Dict
    requirements: List[Dict]
    analysis: Dict
    execution_plan: List[Dict]
    recommendations: List[str]
    final_report: Dict
    error: Optional[str]


class PMRequirementsAgent:
    """
    LangGraph-based AI Agent for analyzing project requirements using Groq.

    This agent uses a graph-based workflow to:
    1. Fetch project and requirement data
    2. Analyze requirement patterns and status
    3. Generate AI-powered execution plans
    4. Provide intelligent recommendations
    5. Create comprehensive reports
    """

    def __init__(self, session: Session):
        self.session = session

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=Config.GROQ_API_KEY,
            max_tokens=4000,
        )

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(RequirementAnalysisState)

        workflow.add_node("fetch_data", self._fetch_data)
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("generate_execution_plan", self._generate_execution_plan)
        workflow.add_node("create_recommendations", self._create_recommendations)
        workflow.add_node("compile_report", self._compile_report)

        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "analyze_requirements")
        workflow.add_edge("analyze_requirements", "generate_execution_plan")
        workflow.add_edge("generate_execution_plan", "create_recommendations")
        workflow.add_edge("create_recommendations", "compile_report")
        workflow.add_edge("compile_report", END)

        return workflow.compile()

    def analyze(
        self, project_id: int, new_requirement_id: Optional[int] = None
    ) -> Dict:
        """
        Run the complete analysis workflow.

        Args:
            project_id: Project ID to analyze
            new_requirement_id: ID of newly added requirement

        Returns:
            dict: Complete analysis report
        """
        try:
            initial_state = RequirementAnalysisState(
                project_id=project_id,
                new_requirement_id=new_requirement_id,
                project_data={},
                requirements=[],
                analysis={},
                execution_plan=[],
                recommendations=[],
                final_report={},
                error=None,
            )

            result = self.graph.invoke(initial_state)

            if result.get("error"):
                return {"error": result["error"]}

            return result["final_report"]

        except Exception as e:
            logger.error(f"Error in requirements analysis: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _fetch_data(self, state: RequirementAnalysisState) -> RequirementAnalysisState:
        """Fetch project and requirement data from database."""
        try:
            project_id = state["project_id"]

            project = self.session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                state["error"] = "Project not found"
                return state

            client = self.session.exec(
                select(Client).where(Client.id == project.client_id)
            ).first()

            requirements = self.session.exec(
                select(Requirement).where(Requirement.project_id == project_id)
            ).all()

            state["project_data"] = {
                "id": project.id,
                "project_id": project.project_id,
                "project_name": project.project_name,
                "description": project.description,
                "status": project.status,
                "client_name": client.client_name if client else "Unknown",
                "client_email": client.email if client else None,
            }

            state["requirements"] = [
                {
                    "id": req.id,
                    "requirement_id": req.requirement_id,
                    "description": req.requirements,
                    "status": req.status,
                    "is_new": req.id == state["new_requirement_id"],
                }
                for req in requirements
            ]

            logger.info(
                f"Fetched {len(requirements)} requirements for project {project_id}"
            )
            return state

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            state["error"] = str(e)
            return state

    def _analyze_requirements(
        self, state: RequirementAnalysisState
    ) -> RequirementAnalysisState:
        """Use AI to analyze requirement patterns and provide insights."""
        try:
            requirements = state["requirements"]
            project = state["project_data"]

            total = len(requirements)
            pending = sum(
                1 for r in requirements if r["status"] == StatusTypeEnum.PENDING
            )
            in_progress = sum(
                1 for r in requirements if r["status"] == StatusTypeEnum.IN_PROGRESS
            )
            completed = sum(
                1 for r in requirements if r["status"] == StatusTypeEnum.COMPLETED
            )
            completion_rate = (completed / total * 100) if total > 0 else 0

            state["analysis"] = {
                "statistics": {
                    "total_requirements": total,
                    "pending": pending,
                    "in_progress": in_progress,
                    "completed": completed,
                    "completion_rate": round(completion_rate, 2),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "ai_analysis": "Analysis in progress...",
            }

            try:

                requirements_text = "\n".join(
                    [
                        f"- [{req['status']}] {req['requirement_id']}: {req['description']}"
                        for req in requirements
                    ]
                )

                new_req_text = ""
                if state["new_requirement_id"]:
                    new_req = next((r for r in requirements if r["is_new"]), None)
                    if new_req:
                        new_req_text = f"\n\nNEW REQUIREMENT JUST ADDED:\n{new_req['requirement_id']}: {new_req['description']}"

                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content="""You are an expert project manager and requirements analyst. 
Analyze project requirements and provide deep insights about:
1. Overall project health and progress
2. Requirement complexity and dependencies
3. Potential risks and blockers
4. Resource allocation needs
5. Timeline implications

Be specific, actionable, and professional."""
                        ),
                        HumanMessage(
                            content=f"""
Project: {project['project_name']}
Status: {project['status']}
Client: {project['client_name']}

Current Requirements:
{requirements_text}
{new_req_text}

Provide a comprehensive analysis of this project's requirements including:
- Overall assessment
- Key patterns or concerns
- Risk factors
- Workload distribution
- Critical path items
"""
                        ),
                    ]
                )

                response = self.llm.invoke(prompt.format_messages())
                state["analysis"]["ai_analysis"] = response.content
                logger.info(
                    f"AI analysis completed for project {project['project_id']}"
                )

            except Exception as ai_error:
                logger.error(f"AI analysis failed: {str(ai_error)}, using fallback")

                state["analysis"]["ai_analysis"] = self._generate_fallback_analysis(
                    project, requirements, state["analysis"]["statistics"]
                )

            return state

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            state["error"] = str(e)
            return state

    def _generate_fallback_analysis(
        self, project: Dict, requirements: List[Dict], stats: Dict
    ) -> str:
        """Generate fallback analysis when AI is unavailable."""
        analysis = f"""
PROJECT ANALYSIS (Rule-Based)

Project: {project['project_name']}
Status: {project['status']}

Overall Assessment:
- Total Requirements: {stats['total_requirements']}
- Completion Rate: {stats['completion_rate']}%

Status Breakdown:
- ✅ Completed: {stats['completed']}
- 🔄 In Progress: {stats['in_progress']}
- ⏳ Pending: {stats['pending']}

Key Observations:
"""

        if stats["completion_rate"] > 70:
            analysis += "\n- Strong progress with over 70% completion"
        elif stats["completion_rate"] > 40:
            analysis += "\n- Moderate progress, requires continued attention"
        else:
            analysis += "\n- Early stage, significant work ahead"

        if stats["in_progress"] > 3:
            analysis += "\n- High concurrent workload detected"

        if stats["pending"] > 5:
            analysis += "\n- Large backlog requires prioritization"

        return analysis

    def _generate_execution_plan(
        self, state: RequirementAnalysisState
    ) -> RequirementAnalysisState:
        """Generate AI-powered execution plan with priorities."""
        try:
            requirements = state["requirements"]
            project = state["project_data"]
            analysis = state["analysis"]

            if "statistics" not in analysis:
                logger.error("Statistics missing, cannot generate execution plan")
                state["error"] = "Statistics not available"
                return state

            pending_reqs = [
                r for r in requirements if r["status"] == StatusTypeEnum.PENDING
            ]
            in_progress_reqs = [
                r for r in requirements if r["status"] == StatusTypeEnum.IN_PROGRESS
            ]
            completed_reqs = [
                r for r in requirements if r["status"] == StatusTypeEnum.COMPLETED
            ]

            execution_plan = []

            if in_progress_reqs:
                execution_plan.append(
                    {
                        "phase": "Phase 1: Complete In-Progress Requirements",
                        "priority": "HIGH",
                        "requirements": [
                            {
                                "requirement_id": r["requirement_id"],
                                "description": r["description"],
                                "status": r["status"],
                            }
                            for r in in_progress_reqs
                        ],
                        "rationale": "Finish ongoing work to maintain momentum and deliver value quickly.",
                        "ai_insights": "Focus on completion before starting new work.",
                    }
                )

            if pending_reqs:
                execution_plan.append(
                    {
                        "phase": "Phase 2: High-Priority New Requirements",
                        "priority": "MEDIUM",
                        "requirements": [
                            {
                                "requirement_id": r["requirement_id"],
                                "description": r["description"],
                                "status": r["status"],
                            }
                            for r in pending_reqs[:3]
                        ],
                        "rationale": "Begin highest-value pending work to maintain project velocity.",
                        "ai_insights": "Prioritize based on business value and dependencies.",
                    }
                )

            state["execution_plan"] = execution_plan

            try:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content="""You are an expert project execution planner.
Create a detailed, phased execution plan that:
1. Prioritizes work strategically
2. Considers dependencies and complexity
3. Balances team workload
4. Minimizes risks
5. Maximizes delivery velocity

Format your response as clear phases with rationale."""
                        ),
                        HumanMessage(
                            content=f"""
Project: {project['project_name']}
Completion Rate: {analysis['statistics']['completion_rate']}%

Requirements Summary:
- Completed: {len(completed_reqs)}
- In Progress: {len(in_progress_reqs)}
- Pending: {len(pending_reqs)}

In Progress Requirements:
{chr(10).join([f"- {r['requirement_id']}: {r['description']}" for r in in_progress_reqs]) if in_progress_reqs else "None"}

Pending Requirements:
{chr(10).join([f"- {r['requirement_id']}: {r['description']}" for r in pending_reqs]) if pending_reqs else "None"}

Create a strategic execution plan with 3-5 clear phases, explaining:
- What to do in each phase
- Priority level (HIGH/MEDIUM/LOW)
- Why this sequence makes sense
- Estimated complexity
"""
                        ),
                    ]
                )

                response = self.llm.invoke(prompt.format_messages())
                state["execution_plan_ai"] = response.content
                logger.info(f"AI execution plan generated")

            except Exception as ai_error:
                logger.error(
                    f"AI execution plan failed: {str(ai_error)}, using basic plan"
                )
                state["execution_plan_ai"] = (
                    "Execution plan generated using rule-based approach."
                )

            return state

        except Exception as e:
            logger.error(f"Error generating execution plan: {str(e)}", exc_info=True)
            state["error"] = str(e)
            return state

    def _create_recommendations(
        self, state: RequirementAnalysisState
    ) -> RequirementAnalysisState:
        """Generate AI-powered recommendations."""
        try:
            project = state["project_data"]
            analysis = state["analysis"]

            if "statistics" not in analysis:
                logger.error("Statistics missing, cannot generate recommendations")
                state["error"] = "Statistics not available"
                return state

            recommendations = []

            if analysis["statistics"]["in_progress"] > 3:
                recommendations.append(
                    "⚠️ HIGH WORKLOAD: Focus on completing in-progress tasks before starting new ones."
                )

            if analysis["statistics"]["completion_rate"] > 70:
                recommendations.append(
                    "✅ EXCELLENT PROGRESS: Project is on track. Maintain current velocity."
                )
            elif analysis["statistics"]["completion_rate"] < 30:
                recommendations.append(
                    "📊 LOW COMPLETION: Review timeline and resource allocation."
                )

            if state["new_requirement_id"]:
                recommendations.append(
                    "🆕 NEW REQUIREMENT: Review impact on timeline and communicate with stakeholders."
                )

            if analysis["statistics"]["pending"] > 5:
                recommendations.append(
                    "📋 LARGE BACKLOG: Prioritize and break down requirements."
                )

            try:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content="""You are a senior project management consultant.
Provide specific, actionable recommendations for:
1. Improving project efficiency
2. Mitigating risks
3. Optimizing team productivity
4. Enhancing quality
5. Meeting deadlines

Be direct and practical. Each recommendation should be implementable."""
                        ),
                        HumanMessage(
                            content=f"""
Project: {project['project_name']}
Status: {project['status']}
Completion Rate: {analysis['statistics']['completion_rate']}%
Total Requirements: {analysis['statistics']['total_requirements']}

In Progress: {analysis['statistics']['in_progress']}
Pending: {analysis['statistics']['pending']}
Completed: {analysis['statistics']['completed']}

Analysis Summary:
{analysis.get('ai_analysis', 'No AI analysis available')[:500]}...

Provide 5-8 specific, actionable recommendations for this project.
Focus on what the PM should do next.
"""
                        ),
                    ]
                )

                response = self.llm.invoke(prompt.format_messages())

                ai_recommendations = [
                    line.strip()
                    for line in response.content.split("\n")
                    if line.strip()
                    and (
                        line.strip().startswith("-")
                        or line.strip().startswith("•")
                        or (len(line.strip()) > 0 and line.strip()[0].isdigit())
                    )
                ]

                recommendations.extend(ai_recommendations[:5])
                logger.info(f"AI recommendations generated")

            except Exception as ai_error:
                logger.error(
                    f"AI recommendations failed: {str(ai_error)}, using basic recommendations"
                )
                recommendations.append(
                    "💡 TIP: Regular status updates help track progress effectively."
                )

            state["recommendations"] = recommendations[:10]
            return state

        except Exception as e:
            logger.error(f"Error creating recommendations: {str(e)}", exc_info=True)
            state["error"] = str(e)
            return state

    def _compile_report(
        self, state: RequirementAnalysisState
    ) -> RequirementAnalysisState:
        """Compile final comprehensive report."""
        try:

            if "analysis" not in state or "statistics" not in state.get("analysis", {}):
                logger.error("Analysis data missing in compile_report")
                state["error"] = "Analysis data missing"
                return state

            new_req = None
            if state["new_requirement_id"]:
                new_req = next((r for r in state["requirements"] if r["is_new"]), None)

            state["final_report"] = {
                "project": state["project_data"],
                "analysis_date": datetime.utcnow().isoformat(),
                "summary": {
                    **state["analysis"]["statistics"],
                    "ai_analysis": state["analysis"].get(
                        "ai_analysis", "No analysis available"
                    ),
                },
                "new_requirement": (
                    {
                        "requirement_id": (
                            new_req["requirement_id"] if new_req else None
                        ),
                        "description": new_req["description"] if new_req else None,
                    }
                    if new_req
                    else None
                ),
                "execution_plan": state.get("execution_plan", []),
                "execution_plan_narrative": state.get("execution_plan_ai", ""),
                "recommendations": state.get("recommendations", []),
                "requirements_details": state["requirements"],
                "generated_by": "AI Agent (Groq + LangGraph)",
                "model": "llama-3.3-70b-versatile",
            }

            logger.info("Final report compiled successfully")
            return state

        except Exception as e:
            logger.error(f"Error compiling report: {str(e)}", exc_info=True)
            state["error"] = str(e)
            return state


def get_pm_requirements_agent(session: Session) -> PMRequirementsAgent:
    """Factory function to create PM requirements agent."""
    return PMRequirementsAgent(session)
