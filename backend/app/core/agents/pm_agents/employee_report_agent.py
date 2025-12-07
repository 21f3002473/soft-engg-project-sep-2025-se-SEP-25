"""
Employee Daily Performance Report Agent using LangGraph
Generates automated daily performance reports for employees with AI analysis.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import TypedDict, Annotated, List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from sqlmodel import Session, select

from app.config import Config
from app.database.connection import get_session
from app.database.product_manager_models import (
    Project,
    EmpTodo,
    StatusTypeEnum,
    UserProject,
)
from app.database import User

logger = logging.getLogger(__name__)


class EmployeeReportState(TypedDict):
    """State for the employee performance report generation workflow"""

    messages: Annotated[list, add_messages]
    employee_id: int
    report_date: str
    employee_data: Dict[str, Any]
    tasks_data: Dict[str, Any]
    projects_data: List[Dict[str, Any]]
    recent_completions: List[Dict[str, Any]]
    summary: str
    achievements: List[str]
    challenges: List[str]
    recommendations: List[str]
    focus_areas: List[str]
    metrics: Dict[str, Any]
    report_body_text: str
    report_body_html: str
    error: str


class EmployeePerformanceAgent:
    """
    LangGraph agent for generating daily employee performance reports.

    Workflow:
    1. Fetch employee data (tasks, projects, recent activity)
    2. Analyze daily performance
    3. Generate achievements list
    4. Identify challenges
    5. Generate recommendations
    6. Suggest focus areas
    7. Calculate metrics
    8. Generate full report (text and HTML)
    """

    def __init__(self, session: Session = None):
        self.session = session or next(get_session())
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=Config.GROQ_API_KEY,
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(EmployeeReportState)

        workflow.add_node("fetch_data", self._fetch_data)
        workflow.add_node("analyze_performance", self._analyze_performance)
        workflow.add_node("generate_achievements", self._generate_achievements)
        workflow.add_node("identify_challenges", self._identify_challenges)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("suggest_focus_areas", self._suggest_focus_areas)
        workflow.add_node("calculate_metrics", self._calculate_metrics)
        workflow.add_node("generate_report", self._generate_report)

        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "analyze_performance")
        workflow.add_edge("analyze_performance", "generate_achievements")
        workflow.add_edge("generate_achievements", "identify_challenges")
        workflow.add_edge("identify_challenges", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "suggest_focus_areas")
        workflow.add_edge("suggest_focus_areas", "calculate_metrics")
        workflow.add_edge("calculate_metrics", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _fetch_data(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 1: Fetch all employee data for the last 24 hours"""
        try:
            logger.info(f"Fetching data for employee {state['employee_id']}")

            employee = self.session.exec(
                select(User).where(User.id == state["employee_id"])
            ).first()

            if not employee:
                state["error"] = f"Employee {state['employee_id']} not found"
                return state

            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            all_tasks = self.session.exec(
                select(EmpTodo).where(EmpTodo.user_id == state["employee_id"])
            ).all()

            user_projects = self.session.exec(
                select(UserProject).where(UserProject.user_id == state["employee_id"])
            ).all()

            project_ids = [up.project_id for up in user_projects]
            projects = []
            if project_ids:
                projects = self.session.exec(
                    select(Project).where(Project.id.in_(project_ids))
                ).all()

            state["employee_data"] = {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "role": employee.role,
            }

            total_tasks = len(all_tasks)
            completed_tasks = sum(
                1 for t in all_tasks if t.status == StatusTypeEnum.COMPLETED
            )
            in_progress_tasks = sum(
                1 for t in all_tasks if t.status == StatusTypeEnum.IN_PROGRESS
            )
            pending_tasks = sum(
                1 for t in all_tasks if t.status == StatusTypeEnum.PENDING
            )

            recent_completed = [
                {
                    "id": t.id,
                    "requirement_id": t.requirement_id,
                    "project_id": t.project_id,
                    "weightage": t.weightage,
                    "status": t.status.value,
                }
                for t in all_tasks
                if t.status == StatusTypeEnum.COMPLETED
            ][:10]

            state["tasks_data"] = {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "pending": pending_tasks,
                "completion_rate": (
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                ),
            }

            state["recent_completions"] = recent_completed

            state["projects_data"] = [
                {
                    "id": p.id,
                    "project_id": p.project_id,
                    "name": p.project_name,
                    "status": p.status.value,
                    "description": p.description,
                }
                for p in projects
            ]

            logger.info(f"Data fetched: {total_tasks} tasks, {len(projects)} projects")

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            state["error"] = str(e)

        return state

    def _analyze_performance(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 2: Analyze daily performance with AI"""
        try:
            logger.info("Analyzing employee performance")

            context = f"""
Employee: {state['employee_data']['name']} ({state['employee_data']['role']})
Report Date: {state['report_date']}

Task Statistics:
- Total Tasks: {state['tasks_data']['total']}
- Completed: {state['tasks_data']['completed']}
- In Progress: {state['tasks_data']['in_progress']}
- Pending: {state['tasks_data']['pending']}
- Completion Rate: {state['tasks_data']['completion_rate']:.1f}%

Projects Assigned: {len(state['projects_data'])}
Project Details: {json.dumps(state['projects_data'], indent=2)}

Recent Completions: {len(state['recent_completions'])} tasks
"""

            prompt = f"""You are an AI performance analyst evaluating an employee's daily work performance.

{context}

Based on the data above, provide a concise performance analysis. Focus on:
1. Overall productivity and work quality
2. Task completion velocity
3. Project involvement and contribution
4. Work distribution across projects

Keep your analysis brief, balanced, and constructive (3-4 sentences)."""

            messages = [
                SystemMessage(
                    content="You are an expert HR and performance management AI assistant."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            state["summary"] = response.content.strip()

            logger.info("Performance analysis completed")

        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}", exc_info=True)
            state["error"] = str(e)

        return state

    def _generate_achievements(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 3: Generate list of achievements"""
        try:
            logger.info("Generating achievements list")

            context = f"""
Employee: {state['employee_data']['name']}
Tasks Completed: {state['tasks_data']['completed']}
Recent Completions: {json.dumps(state['recent_completions'][:5], indent=2)}
Projects: {len(state['projects_data'])} active projects
"""

            prompt = f"""Based on the employee's work activity below, identify key achievements.

{context}

List 3-5 specific achievements or accomplishments. Each should be:
- Concrete and measurable
- Highlight completed work or milestones
- Professional and motivating
- One sentence each

Return ONLY a JSON array of strings:
["achievement 1", "achievement 2", ...]

If limited visible achievements, mention steady progress and reliability."""

            messages = [
                SystemMessage(
                    content="You are an AI that extracts achievements from work data. Respond ONLY with valid JSON."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            content = response.content.strip()

            try:
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                achievements = json.loads(content)
                state["achievements"] = (
                    achievements
                    if isinstance(achievements, list)
                    else [str(achievements)]
                )
            except json.JSONDecodeError:
                state["achievements"] = ["Maintained consistent work progress"]

            logger.info(f"Generated {len(state['achievements'])} achievements")

        except Exception as e:
            logger.error(f"Error generating achievements: {str(e)}", exc_info=True)
            state["achievements"] = ["Continued assigned work tasks"]

        return state

    def _identify_challenges(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 4: Identify challenges or areas of concern"""
        try:
            logger.info("Identifying challenges")

            context = f"""
Employee: {state['employee_data']['name']}
In Progress Tasks: {state['tasks_data']['in_progress']}
Pending Tasks: {state['tasks_data']['pending']}
Completion Rate: {state['tasks_data']['completion_rate']:.1f}%
Projects Count: {len(state['projects_data'])}
"""

            prompt = f"""Analyze potential challenges or areas where the employee might need support.

{context}

Consider:
- Task load and capacity
- Completion rate trends
- Multi-project juggling
- Pending work accumulation

List 0-3 constructive challenges or concerns. Each should be:
- Observation-based, not judgmental
- Actionable
- Professionally framed

Return ONLY a JSON array of strings:
["challenge 1", "challenge 2", ...]

If everything looks good, return ["No significant challenges identified"]"""

            messages = [
                SystemMessage(
                    content="You are an AI that identifies work challenges constructively. Respond ONLY with valid JSON."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            content = response.content.strip()

            try:
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                challenges = json.loads(content)
                state["challenges"] = (
                    challenges if isinstance(challenges, list) else [str(challenges)]
                )
            except json.JSONDecodeError:
                state["challenges"] = ["No significant challenges identified"]

            logger.info(f"Identified {len(state['challenges'])} challenges")

        except Exception as e:
            logger.error(f"Error identifying challenges: {str(e)}", exc_info=True)
            state["challenges"] = ["Unable to assess challenges"]

        return state

    def _generate_recommendations(
        self, state: EmployeeReportState
    ) -> EmployeeReportState:
        """Node 5: Generate improvement recommendations"""
        try:
            logger.info("Generating recommendations")

            context = f"""
Employee: {state['employee_data']['name']}
Current Performance: {state['tasks_data']['completion_rate']:.1f}% completion rate
Challenges: {json.dumps(state['challenges'])}
Projects: {len(state['projects_data'])}
"""

            prompt = f"""Based on the performance data, suggest 2-4 recommendations for improvement or growth.

{context}

Each recommendation should be:
- Actionable and specific
- Supportive and constructive
- Focused on growth and development
- Realistic and achievable

Return ONLY a JSON array of strings:
["recommendation 1", "recommendation 2", ...]"""

            messages = [
                SystemMessage(
                    content="You are an AI career development advisor. Respond ONLY with valid JSON."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            content = response.content.strip()

            try:
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                recommendations = json.loads(content)
                state["recommendations"] = (
                    recommendations
                    if isinstance(recommendations, list)
                    else [str(recommendations)]
                )
            except json.JSONDecodeError:
                state["recommendations"] = ["Continue current work approach"]

            logger.info(f"Generated {len(state['recommendations'])} recommendations")

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            state["recommendations"] = ["Maintain current performance standards"]

        return state

    def _suggest_focus_areas(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 6: Suggest focus areas for next period"""
        try:
            logger.info("Suggesting focus areas")

            context = f"""
Employee: {state['employee_data']['name']}
Pending Tasks: {state['tasks_data']['pending']}
In Progress: {state['tasks_data']['in_progress']}
Projects: {json.dumps(state['projects_data'], indent=2)}
"""

            prompt = f"""Based on current workload, suggest 3-4 focus areas for the next 24 hours.

{context}

Each focus area should be:
- Specific to their assigned work
- Prioritized (most important first)
- Clear and actionable
- Achievable in the timeframe

Return ONLY a JSON array of strings:
["focus area 1", "focus area 2", ...]"""

            messages = [
                SystemMessage(
                    content="You are an AI work prioritization assistant. Respond ONLY with valid JSON."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            content = response.content.strip()

            try:
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                focus_areas = json.loads(content)
                state["focus_areas"] = (
                    focus_areas if isinstance(focus_areas, list) else [str(focus_areas)]
                )
            except json.JSONDecodeError:
                state["focus_areas"] = ["Continue with assigned tasks"]

            logger.info(f"Generated {len(state['focus_areas'])} focus areas")

        except Exception as e:
            logger.error(f"Error suggesting focus areas: {str(e)}", exc_info=True)
            state["focus_areas"] = ["Proceed with current task priorities"]

        return state

    def _calculate_metrics(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 7: Calculate performance metrics"""
        try:
            logger.info("Calculating metrics")

            completion_rate = state["tasks_data"]["completion_rate"]
            in_progress_ratio = (
                (
                    state["tasks_data"]["in_progress"]
                    / state["tasks_data"]["total"]
                    * 100
                )
                if state["tasks_data"]["total"] > 0
                else 0
            )

            productivity_score = min(
                100, (completion_rate * 0.7) + (in_progress_ratio * 0.3)
            )

            state["metrics"] = {
                "tasks_completed_today": state["tasks_data"]["completed"],
                "tasks_in_progress": state["tasks_data"]["in_progress"],
                "tasks_pending": state["tasks_data"]["pending"],
                "total_tasks": state["tasks_data"]["total"],
                "completion_rate": round(completion_rate, 1),
                "projects_count": len(state["projects_data"]),
                "productivity_score": round(productivity_score, 1),
                "recent_completions_count": len(state["recent_completions"]),
            }

            logger.info(f"Metrics calculated: {state['metrics']}")

        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}", exc_info=True)
            state["metrics"] = {}

        return state

    def _generate_report(self, state: EmployeeReportState) -> EmployeeReportState:
        """Node 8: Generate full report in text and HTML format"""
        try:
            logger.info("Generating full report")

            text_report = f"""
Daily Employee Performance Report
==================================

Employee: {state['employee_data']['name']}
Email: {state['employee_data']['email']}
Role: {state['employee_data']['role']}
Report Date: {state['report_date']}

PERFORMANCE SUMMARY
-------------------
{state['summary']}

KEY ACHIEVEMENTS
----------------
"""
            for i, achievement in enumerate(state["achievements"], 1):
                text_report += f"{i}. {achievement}\n"

            text_report += f"""
CHALLENGES & CONCERNS
---------------------
"""
            for i, challenge in enumerate(state["challenges"], 1):
                text_report += f"{i}. {challenge}\n"

            text_report += f"""
RECOMMENDATIONS
---------------
"""
            for i, rec in enumerate(state["recommendations"], 1):
                text_report += f"{i}. {rec}\n"

            text_report += f"""
FOCUS AREAS (Next 24 Hours)
----------------------------
"""
            for i, focus in enumerate(state["focus_areas"], 1):
                text_report += f"{i}. {focus}\n"

            text_report += f"""
PERFORMANCE METRICS
-------------------
Tasks Completed: {state['metrics']['tasks_completed_today']}
Tasks In Progress: {state['metrics']['tasks_in_progress']}
Tasks Pending: {state['metrics']['tasks_pending']}
Total Tasks: {state['metrics']['total_tasks']}
Completion Rate: {state['metrics']['completion_rate']}%
Projects Active: {state['metrics']['projects_count']}
Productivity Score: {state['metrics']['productivity_score']}/100

---
Generated automatically by PM AI Assistant
"""

            state["report_body_text"] = text_report

            html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea; }}
        .section h2 {{ margin-top: 0; color: #667eea; font-size: 20px; }}
        .achievement {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #28a745; }}
        .challenge {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #ffc107; }}
        .recommendation {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #17a2b8; }}
        .focus {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #6f42c1; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .summary-box {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196f3; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
        .score-badge {{ display: inline-block; background: #28a745; color: white; padding: 8px 16px; border-radius: 20px; font-size: 18px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👤 Daily Performance Report</h1>
        <p><strong>Employee:</strong> {state['employee_data']['name']}</p>
        <p><strong>Role:</strong> {state['employee_data']['role']}</p>
        <p><strong>Date:</strong> {state['report_date']}</p>
        <p style="margin-top: 10px;">
            <span class="score-badge">Productivity: {state['metrics']['productivity_score']}/100</span>
        </p>
    </div>
    
    <div class="summary-box">
        <h2 style="margin-top: 0; color: #2196f3;">📊 Performance Summary</h2>
        <p style="margin: 0;">{state['summary']}</p>
    </div>
    
    <div class="section">
        <h2>🏆 Key Achievements</h2>
"""
            for achievement in state["achievements"]:
                html_report += (
                    f'        <div class="achievement">✓ {achievement}</div>\n'
                )

            html_report += """    </div>
    
    <div class="section">
        <h2>⚠️ Challenges & Concerns</h2>
"""
            for challenge in state["challenges"]:
                html_report += f'        <div class="challenge">• {challenge}</div>\n'

            html_report += """    </div>
    
    <div class="section">
        <h2>💡 Recommendations</h2>
"""
            for rec in state["recommendations"]:
                html_report += f'        <div class="recommendation">→ {rec}</div>\n'

            html_report += """    </div>
    
    <div class="section">
        <h2>🎯 Focus Areas (Next 24 Hours)</h2>
"""
            for focus in state["focus_areas"]:
                html_report += f'        <div class="focus">• {focus}</div>\n'

            html_report += f"""    </div>
    
    <div class="section">
        <h2>📈 Performance Metrics</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['tasks_completed_today']}</div>
                <div class="metric-label">Completed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['tasks_in_progress']}</div>
                <div class="metric-label">In Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['tasks_pending']}</div>
                <div class="metric-label">Pending</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['completion_rate']}%</div>
                <div class="metric-label">Completion Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['projects_count']}</div>
                <div class="metric-label">Active Projects</div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated automatically by PM AI Assistant</p>
        <p>© {datetime.now().year} Performance Management System</p>
    </div>
</body>
</html>
"""

            state["report_body_html"] = html_report

            logger.info("Full report generated successfully")

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            state["error"] = str(e)

        return state

    def generate_employee_report(
        self, employee_id: int, report_date: str = None
    ) -> Dict[str, Any]:
        """
        Main method to generate an employee performance report.

        Args:
            employee_id: Employee ID
            report_date: Date for the report (defaults to today)

        Returns:
            dict: Generated report data
        """
        try:
            if not report_date:
                report_date = datetime.now().strftime("%Y-%m-%d")

            logger.info(
                f"Starting employee report generation for employee {employee_id}"
            )

            initial_state = {
                "messages": [],
                "employee_id": employee_id,
                "report_date": report_date,
                "employee_data": {},
                "tasks_data": {},
                "projects_data": [],
                "recent_completions": [],
                "summary": "",
                "achievements": [],
                "challenges": [],
                "recommendations": [],
                "focus_areas": [],
                "metrics": {},
                "report_body_text": "",
                "report_body_html": "",
                "error": "",
            }

            final_state = self.graph.invoke(initial_state)

            if final_state.get("error"):
                logger.error(f"Error in workflow: {final_state['error']}")
                return {"success": False, "error": final_state["error"]}

            logger.info("Employee report generated successfully")

            return {
                "success": True,
                "employee_id": employee_id,
                "report_date": report_date,
                "summary": final_state["summary"],
                "achievements": final_state["achievements"],
                "challenges": final_state["challenges"],
                "recommendations": final_state["recommendations"],
                "focus_areas": final_state["focus_areas"],
                "metrics": final_state["metrics"],
                "report_body_text": final_state["report_body_text"],
                "report_body_html": final_state["report_body_html"],
                "tasks_count": final_state["tasks_data"]["total"],
                "projects_count": len(final_state["projects_data"]),
            }

        except Exception as e:
            logger.error(
                f"Fatal error generating employee report: {str(e)}", exc_info=True
            )
            return {"success": False, "error": str(e)}
