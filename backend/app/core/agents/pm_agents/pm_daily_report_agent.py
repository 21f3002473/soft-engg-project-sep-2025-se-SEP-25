"""
PM Daily Report Agent using LangGraph
Generates automated daily progress reports for projects with AI analysis.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, List, TypedDict

from app.config import Config
from app.database.connection import get_session
from app.database.product_manager_models import (
    Client,
    EmpTodo,
    Project,
    ProjectDailyReport,
    Requirement,
    StatusTypeEnum,
    Update,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class DailyReportState(TypedDict):
    """State for the daily report generation workflow"""

    messages: Annotated[list, add_messages]
    project_id: int
    client_id: int
    report_date: str
    project_data: Dict[str, Any]
    recent_updates: List[Dict[str, Any]]
    requirements_data: Dict[str, Any]
    todos_data: Dict[str, Any]
    summary: str
    achievements: List[str]
    blockers: List[str]
    upcoming_tasks: List[str]
    metrics: Dict[str, Any]
    report_body_text: str
    report_body_html: str
    error: str


class PMDailyReportAgent:
    """
    LangGraph agent for generating daily project progress reports.

    Workflow:
    1. Fetch project data (updates, requirements, todos from last 24h)
    2. Analyze daily progress and identify patterns
    3. Generate achievements list
    4. Identify blockers and issues
    5. List upcoming tasks
    6. Calculate metrics
    7. Generate full report (text and HTML)
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
        workflow = StateGraph(DailyReportState)

        workflow.add_node("fetch_data", self._fetch_data)
        workflow.add_node("analyze_progress", self._analyze_progress)
        workflow.add_node("generate_achievements", self._generate_achievements)
        workflow.add_node("identify_blockers", self._identify_blockers)
        workflow.add_node("plan_upcoming", self._plan_upcoming)
        workflow.add_node("calculate_metrics", self._calculate_metrics)
        workflow.add_node("generate_report", self._generate_report)

        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "analyze_progress")
        workflow.add_edge("analyze_progress", "generate_achievements")
        workflow.add_edge("generate_achievements", "identify_blockers")
        workflow.add_edge("identify_blockers", "plan_upcoming")
        workflow.add_edge("plan_upcoming", "calculate_metrics")
        workflow.add_edge("calculate_metrics", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _fetch_data(self, state: DailyReportState) -> DailyReportState:
        """Node 1: Fetch all project data for the last 24 hours"""
        try:
            logger.info(f"Fetching data for project {state['project_id']}")

            project = self.session.exec(
                select(Project).where(Project.id == state["project_id"])
            ).first()

            if not project:
                state["error"] = f"Project {state['project_id']} not found"
                return state

            client = self.session.exec(
                select(Client).where(Client.id == state["client_id"])
            ).first()

            if not client:
                state["error"] = f"Client {state['client_id']} not found"
                return state

            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            updates = self.session.exec(
                select(Update)
                .where(Update.project_id == state["project_id"])
                .where(Update.date >= start_date)
                .order_by(Update.date.desc())
            ).all()

            requirements = self.session.exec(
                select(Requirement).where(Requirement.project_id == state["project_id"])
            ).all()

            todos = self.session.exec(
                select(EmpTodo).where(EmpTodo.project_id == state["project_id"])
            ).all()

            state["project_data"] = {
                "id": project.id,
                "project_id": project.project_id,
                "name": project.project_name,
                "description": project.description,
                "status": project.status.value,
                "client_name": client.client_name,
                "client_email": client.email,
            }

            state["recent_updates"] = [
                {
                    "id": u.id,
                    "update_id": u.update_id,
                    "details": u.details,
                    "date": u.date.isoformat(),
                }
                for u in updates
            ]

            total_reqs = len(requirements)
            completed_reqs = sum(
                1 for r in requirements if r.status == StatusTypeEnum.COMPLETED
            )
            in_progress_reqs = sum(
                1 for r in requirements if r.status == StatusTypeEnum.IN_PROGRESS
            )
            pending_reqs = sum(
                1 for r in requirements if r.status == StatusTypeEnum.PENDING
            )

            state["requirements_data"] = {
                "total": total_reqs,
                "completed": completed_reqs,
                "in_progress": in_progress_reqs,
                "pending": pending_reqs,
                "completion_rate": (
                    (completed_reqs / total_reqs * 100) if total_reqs > 0 else 0
                ),
            }

            total_todos = len(todos)
            completed_todos = sum(
                1 for t in todos if t.status == StatusTypeEnum.COMPLETED
            )
            in_progress_todos = sum(
                1 for t in todos if t.status == StatusTypeEnum.IN_PROGRESS
            )
            pending_todos = sum(1 for t in todos if t.status == StatusTypeEnum.PENDING)

            state["todos_data"] = {
                "total": total_todos,
                "completed": completed_todos,
                "in_progress": in_progress_todos,
                "pending": pending_todos,
                "completion_rate": (
                    (completed_todos / total_todos * 100) if total_todos > 0 else 0
                ),
            }

            logger.info(
                f"Data fetched: {len(updates)} updates, {total_reqs} requirements, {total_todos} todos"
            )

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            state["error"] = str(e)

        return state

    def _analyze_progress(self, state: DailyReportState) -> DailyReportState:
        """Node 2: Analyze daily progress with AI"""
        try:
            logger.info("Analyzing daily progress")

            context = f"""
Project: {state['project_data']['name']}
Status: {state['project_data']['status']}
Report Date: {state['report_date']}

Recent Updates (Last 24h): {len(state['recent_updates'])} updates
{json.dumps(state['recent_updates'], indent=2)}

Requirements Progress:
- Total: {state['requirements_data']['total']}
- Completed: {state['requirements_data']['completed']}
- In Progress: {state['requirements_data']['in_progress']}
- Pending: {state['requirements_data']['pending']}
- Completion Rate: {state['requirements_data']['completion_rate']:.1f}%

Tasks Progress:
- Total: {state['todos_data']['total']}
- Completed: {state['todos_data']['completed']}
- In Progress: {state['todos_data']['in_progress']}
- Pending: {state['todos_data']['pending']}
- Completion Rate: {state['todos_data']['completion_rate']:.1f}%
"""

            prompt = f"""You are an AI project manager analyzing daily progress for a software project.

{context}

Based on the data above, provide a concise analysis of today's progress. Focus on:
1. Overall progress trend
2. Velocity and momentum
3. Any concerns or risks
4. Positive developments

Keep your analysis brief, factual, and actionable (3-4 sentences)."""

            messages = [
                SystemMessage(
                    content="You are an expert project management AI assistant."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            state["summary"] = response.content.strip()

            logger.info("Progress analysis completed")

        except Exception as e:
            logger.error(f"Error analyzing progress: {str(e)}", exc_info=True)
            state["error"] = str(e)

        return state

    def _generate_achievements(self, state: DailyReportState) -> DailyReportState:
        """Node 3: Generate list of achievements"""
        try:
            logger.info("Generating achievements list")

            context = f"""
Project: {state['project_data']['name']}
Recent Updates: {json.dumps(state['recent_updates'], indent=2)}
Requirements Completed: {state['requirements_data']['completed']}
Tasks Completed Today: {state['todos_data']['completed']}
"""

            prompt = f"""Based on the project activity below, identify key achievements from the last 24 hours.

{context}

List 3-5 concrete achievements. Each achievement should be:
- Specific and measurable
- Highlight completed work or milestones
- Be clear and concise (one sentence each)

Return ONLY a JSON array of strings, no additional text:
["achievement 1", "achievement 2", ...]

If there are no significant achievements, return ["Routine project maintenance and monitoring"]"""

            messages = [
                SystemMessage(
                    content="You are an AI that extracts achievements from project data. Respond ONLY with valid JSON."
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
                state["achievements"] = ["Progress updates recorded"]

            logger.info(f"Generated {len(state['achievements'])} achievements")

        except Exception as e:
            logger.error(f"Error generating achievements: {str(e)}", exc_info=True)
            state["achievements"] = ["Error generating achievements"]

        return state

    def _identify_blockers(self, state: DailyReportState) -> DailyReportState:
        """Node 4: Identify blockers and issues"""
        try:
            logger.info("Identifying blockers")

            context = f"""
Project: {state['project_data']['name']}
Status: {state['project_data']['status']}
In Progress Requirements: {state['requirements_data']['in_progress']}
Pending Requirements: {state['requirements_data']['pending']}
In Progress Tasks: {state['todos_data']['in_progress']}
Updates Count (24h): {len(state['recent_updates'])}
"""

            prompt = f"""Analyze the project status and identify potential blockers or concerns.

{context}

Consider:
- Low update frequency might indicate blocked progress
- High pending/in-progress ratios might indicate capacity issues
- Project status concerns

List 0-3 potential blockers or concerns. Each should be:
- Actionable and specific
- Based on observable data
- Constructive (suggest what to watch or do)

Return ONLY a JSON array of strings:
["blocker 1", "blocker 2", ...]

If everything looks good, return ["No significant blockers identified"]"""

            messages = [
                SystemMessage(
                    content="You are an AI that identifies project risks. Respond ONLY with valid JSON."
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

                blockers = json.loads(content)
                state["blockers"] = (
                    blockers if isinstance(blockers, list) else [str(blockers)]
                )
            except json.JSONDecodeError:
                state["blockers"] = ["No significant blockers identified"]

            logger.info(f"Identified {len(state['blockers'])} blockers")

        except Exception as e:
            logger.error(f"Error identifying blockers: {str(e)}", exc_info=True)
            state["blockers"] = ["Unable to assess blockers"]

        return state

    def _plan_upcoming(self, state: DailyReportState) -> DailyReportState:
        """Node 5: Suggest upcoming tasks and focus areas"""
        try:
            logger.info("Planning upcoming tasks")

            context = f"""
Project: {state['project_data']['name']}
Status: {state['project_data']['status']}
Pending Requirements: {state['requirements_data']['pending']}
In Progress Requirements: {state['requirements_data']['in_progress']}
Pending Tasks: {state['todos_data']['pending']}
In Progress Tasks: {state['todos_data']['in_progress']}
"""

            prompt = f"""Based on the current project state, suggest 3-5 focus areas or upcoming tasks for the next 24 hours.

{context}

Each suggestion should be:
- Actionable and specific
- Prioritized (most important first)
- Realistic for a 24-hour timeframe

Return ONLY a JSON array of strings:
["task 1", "task 2", ...]"""

            messages = [
                SystemMessage(
                    content="You are an AI project planner. Respond ONLY with valid JSON."
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

                upcoming = json.loads(content)
                state["upcoming_tasks"] = (
                    upcoming if isinstance(upcoming, list) else [str(upcoming)]
                )
            except json.JSONDecodeError:
                state["upcoming_tasks"] = ["Continue with planned work"]

            logger.info(f"Generated {len(state['upcoming_tasks'])} upcoming tasks")

        except Exception as e:
            logger.error(f"Error planning upcoming tasks: {str(e)}", exc_info=True)
            state["upcoming_tasks"] = ["Continue with current work"]

        return state

    def _calculate_metrics(self, state: DailyReportState) -> DailyReportState:
        """Node 6: Calculate project metrics"""
        try:
            logger.info("Calculating metrics")

            state["metrics"] = {
                "updates_last_24h": len(state["recent_updates"]),
                "total_requirements": state["requirements_data"]["total"],
                "completed_requirements": state["requirements_data"]["completed"],
                "requirements_completion_rate": round(
                    state["requirements_data"]["completion_rate"], 1
                ),
                "total_tasks": state["todos_data"]["total"],
                "completed_tasks": state["todos_data"]["completed"],
                "tasks_completion_rate": round(
                    state["todos_data"]["completion_rate"], 1
                ),
                "overall_completion": (
                    round(
                        (
                            state["requirements_data"]["completion_rate"]
                            + state["todos_data"]["completion_rate"]
                        )
                        / 2,
                        1,
                    )
                    if state["requirements_data"]["total"] > 0
                    or state["todos_data"]["total"] > 0
                    else 0
                ),
            }

            logger.info(f"Metrics calculated: {state['metrics']}")

        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}", exc_info=True)
            state["metrics"] = {}

        return state

    def _generate_report(self, state: DailyReportState) -> DailyReportState:
        """Node 7: Generate full report in text and HTML format"""
        try:
            logger.info("Generating full report")

            text_report = f"""
Daily Project Progress Report
=============================

Project: {state['project_data']['name']}
Client: {state['project_data']['client_name']}
Report Date: {state['report_date']}
Status: {state['project_data']['status']}

EXECUTIVE SUMMARY
-----------------
{state['summary']}

KEY ACHIEVEMENTS (Last 24 Hours)
---------------------------------
"""
            for i, achievement in enumerate(state["achievements"], 1):
                text_report += f"{i}. {achievement}\n"

            text_report += f"""
BLOCKERS & CONCERNS
-------------------
"""
            for i, blocker in enumerate(state["blockers"], 1):
                text_report += f"{i}. {blocker}\n"

            text_report += f"""
UPCOMING FOCUS AREAS (Next 24 Hours)
-------------------------------------
"""
            for i, task in enumerate(state["upcoming_tasks"], 1):
                text_report += f"{i}. {task}\n"

            text_report += f"""
PROJECT METRICS
---------------
Updates (24h): {state['metrics']['updates_last_24h']}
Requirements: {state['metrics']['completed_requirements']}/{state['metrics']['total_requirements']} ({state['metrics']['requirements_completion_rate']}%)
Tasks: {state['metrics']['completed_tasks']}/{state['metrics']['total_tasks']} ({state['metrics']['tasks_completion_rate']}%)
Overall Completion: {state['metrics']['overall_completion']}%

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
        .blocker {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #ffc107; }}
        .upcoming {{ background: white; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 3px solid #17a2b8; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .summary-box {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196f3; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Daily Project Progress Report</h1>
        <p><strong>Project:</strong> {state['project_data']['name']}</p>
        <p><strong>Client:</strong> {state['project_data']['client_name']}</p>
        <p><strong>Date:</strong> {state['report_date']} | <strong>Status:</strong> {state['project_data']['status']}</p>
    </div>
    
    <div class="summary-box">
        <h2 style="margin-top: 0; color: #2196f3;">📋 Executive Summary</h2>
        <p style="margin: 0;">{state['summary']}</p>
    </div>
    
    <div class="section">
        <h2>✅ Key Achievements (Last 24 Hours)</h2>
"""
            for achievement in state["achievements"]:
                html_report += (
                    f'        <div class="achievement">✓ {achievement}</div>\n'
                )

            html_report += """    </div>
    
    <div class="section">
        <h2>⚠️ Blockers & Concerns</h2>
"""
            for blocker in state["blockers"]:
                html_report += f'        <div class="blocker">• {blocker}</div>\n'

            html_report += """    </div>
    
    <div class="section">
        <h2>🎯 Upcoming Focus Areas (Next 24 Hours)</h2>
"""
            for task in state["upcoming_tasks"]:
                html_report += f'        <div class="upcoming">→ {task}</div>\n'

            html_report += f"""    </div>
    
    <div class="section">
        <h2>📈 Project Metrics</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['updates_last_24h']}</div>
                <div class="metric-label">Updates (24h)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['requirements_completion_rate']}%</div>
                <div class="metric-label">Requirements Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['tasks_completion_rate']}%</div>
                <div class="metric-label">Tasks Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state['metrics']['overall_completion']}%</div>
                <div class="metric-label">Overall Completion</div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated automatically by PM AI Assistant</p>
        <p>© {datetime.now().year} Project Management System</p>
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

    def generate_daily_report(
        self, project_id: int, client_id: int, report_date: str = None
    ) -> Dict[str, Any]:
        """
        Main method to generate a daily report.

        Args:
            project_id: Project ID
            client_id: Client ID
            report_date: Date for the report (defaults to today)

        Returns:
            dict: Generated report data
        """
        try:
            if not report_date:
                report_date = datetime.now().strftime("%Y-%m-%d")

            logger.info(f"Starting daily report generation for project {project_id}")

            initial_state = {
                "messages": [],
                "project_id": project_id,
                "client_id": client_id,
                "report_date": report_date,
                "project_data": {},
                "recent_updates": [],
                "requirements_data": {},
                "todos_data": {},
                "summary": "",
                "achievements": [],
                "blockers": [],
                "upcoming_tasks": [],
                "metrics": {},
                "report_body_text": "",
                "report_body_html": "",
                "error": "",
            }

            final_state = self.graph.invoke(initial_state)

            if final_state.get("error"):
                logger.error(f"Error in workflow: {final_state['error']}")
                return {"success": False, "error": final_state["error"]}

            logger.info("Daily report generated successfully")

            return {
                "success": True,
                "project_id": project_id,
                "client_id": client_id,
                "report_date": report_date,
                "summary": final_state["summary"],
                "achievements": final_state["achievements"],
                "blockers": final_state["blockers"],
                "upcoming_tasks": final_state["upcoming_tasks"],
                "metrics": final_state["metrics"],
                "report_body_text": final_state["report_body_text"],
                "report_body_html": final_state["report_body_html"],
                "updates_count": len(final_state["recent_updates"]),
                "update_ids": [u["id"] for u in final_state["recent_updates"]],
            }

        except Exception as e:
            logger.error(
                f"Fatal error generating daily report: {str(e)}", exc_info=True
            )
            return {"success": False, "error": str(e)}
