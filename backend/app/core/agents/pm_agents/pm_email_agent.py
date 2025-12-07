"""
LangGraph-based AI Agent for generating client progress emails.

This agent creates personalized progress update emails for clients
using project updates, requirements status, and milestone information.
"""

import logging
import json
from typing import Annotated, Dict, List, Optional, TypedDict
from datetime import datetime, timedelta

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.config import Config
from app.database.product_manager_models import (
    Project,
    Client,
    Update,
    Requirement,
    StatusTypeEnum,
    ClientProgressEmail,
)
from sqlmodel import Session, select, desc

logger = logging.getLogger(__name__)


class EmailGenerationState(TypedDict):
    """State for the email generation workflow."""

    project_id: int
    client_id: int
    project_data: Dict
    client_data: Dict
    recent_updates: List[Dict]
    requirements_summary: Dict
    progress_analysis: Dict
    email_subject: str
    email_body: str
    email_html: str
    error: Optional[str]


class PMClientEmailAgent:
    """
    LangGraph-based AI Agent for generating client progress emails.

    This agent creates professional, personalized emails that:
    1. Summarize recent project updates
    2. Analyze requirement completion status
    3. Highlight achievements and milestones
    4. Provide timeline and next steps
    5. Maintain professional tone
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
        """Build the LangGraph workflow for email generation."""
        workflow = StateGraph(EmailGenerationState)

        workflow.add_node("fetch_data", self._fetch_data)
        workflow.add_node("analyze_progress", self._analyze_progress)
        workflow.add_node("generate_subject", self._generate_subject)
        workflow.add_node("generate_body", self._generate_body)
        workflow.add_node("generate_html", self._generate_html)

        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "analyze_progress")
        workflow.add_edge("analyze_progress", "generate_subject")
        workflow.add_edge("generate_subject", "generate_body")
        workflow.add_edge("generate_body", "generate_html")
        workflow.add_edge("generate_html", END)

        return workflow.compile()

    def generate_email(
        self, project_id: int, client_id: int, trigger_type: str = "manual"
    ) -> Dict:
        """
        Generate a complete progress email.

        Args:
            project_id: Project ID
            client_id: Client ID
            trigger_type: What triggered the email generation

        Returns:
            dict: Complete email with subject, body, and HTML
        """
        try:
            initial_state = EmailGenerationState(
                project_id=project_id,
                client_id=client_id,
                project_data={},
                client_data={},
                recent_updates=[],
                requirements_summary={},
                progress_analysis={},
                email_subject="",
                email_body="",
                email_html="",
                error=None,
            )

            logger.info(
                f"Starting email generation for project {project_id}, client {client_id}"
            )

            final_state = self.graph.invoke(initial_state)

            if final_state.get("error"):
                logger.error(f"Email generation failed: {final_state['error']}")
                return {"error": final_state["error"]}

            self._save_email(final_state, trigger_type)

            return {
                "subject": final_state["email_subject"],
                "body_text": final_state["email_body"],
                "body_html": final_state["email_html"],
                "project": final_state["project_data"],
                "client": final_state["client_data"],
            }

        except Exception as e:
            logger.error(f"Error in email generation: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _fetch_data(self, state: EmailGenerationState) -> EmailGenerationState:
        """Fetch project, client, updates, and requirements data."""
        try:
            project_id = state["project_id"]
            client_id = state["client_id"]

            project = self.session.exec(
                select(Project).where(Project.id == project_id)
            ).first()

            if not project:
                state["error"] = "Project not found"
                return state

            client = self.session.exec(
                select(Client).where(Client.id == client_id)
            ).first()

            if not client:
                state["error"] = "Client not found"
                return state

            thirty_days_ago = datetime.now() - timedelta(days=30)
            updates = self.session.exec(
                select(Update)
                .where(Update.project_id == project_id)
                .where(Update.date >= thirty_days_ago)
                .order_by(desc(Update.date))
            ).all()

            requirements = self.session.exec(
                select(Requirement).where(Requirement.project_id == project_id)
            ).all()

            state["project_data"] = {
                "id": project.id,
                "project_id": project.project_id,
                "project_name": project.project_name,
                "description": project.description,
                "status": project.status,
            }

            state["client_data"] = {
                "id": client.id,
                "client_id": client.client_id,
                "client_name": client.client_name,
                "email": client.email,
            }

            state["recent_updates"] = [
                {
                    "id": upd.id,
                    "update_id": upd.update_id,
                    "details": upd.details,
                    "date": upd.date.isoformat(),
                }
                for upd in updates
            ]

            total = len(requirements)
            pending = sum(1 for r in requirements if r.status == StatusTypeEnum.PENDING)
            in_progress = sum(
                1 for r in requirements if r.status == StatusTypeEnum.IN_PROGRESS
            )
            completed = sum(
                1 for r in requirements if r.status == StatusTypeEnum.COMPLETED
            )

            state["requirements_summary"] = {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
                "completion_percentage": round(
                    (completed / total * 100) if total > 0 else 0, 1
                ),
            }

            logger.info(
                f"Fetched {len(updates)} updates and {total} requirements for project {project_id}"
            )

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", exc_info=True)
            state["error"] = f"Data fetch error: {str(e)}"

        return state

    def _analyze_progress(self, state: EmailGenerationState) -> EmailGenerationState:
        """Use AI to analyze project progress and generate insights."""
        try:
            project_data = state["project_data"]
            updates = state["recent_updates"]
            req_summary = state["requirements_summary"]

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content="""You are an expert project analyst creating progress analysis for client communication.
Analyze the project data and provide:
1. Overall project health assessment
2. Key accomplishments in recent updates
3. Completion velocity and trends
4. Potential risks or concerns
5. Next milestone predictions

Provide analysis in JSON format:
{
    "health_status": "on_track|at_risk|delayed",
    "health_reason": "brief explanation",
    "key_accomplishments": ["achievement 1", "achievement 2", ...],
    "progress_trend": "accelerating|steady|slowing",
    "concerns": ["concern 1", ...] or [],
    "next_milestones": ["milestone 1", ...]
}
"""
                    ),
                    HumanMessage(
                        content=f"""Project: {project_data['project_name']}
Status: {project_data['status']}

Requirements Summary:
- Total: {req_summary['total']}
- Completed: {req_summary['completed']} ({req_summary['completion_percentage']}%)
- In Progress: {req_summary['in_progress']}
- Pending: {req_summary['pending']}

Recent Updates ({len(updates)} updates):
{json.dumps(updates[:10], indent=2)}

Analyze this project's progress."""
                    ),
                ]
            )

            messages = prompt.format_messages()
            response = self.llm.invoke(messages)

            try:
                content = str(response.content)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                analysis = json.loads(content)
                state["progress_analysis"] = analysis

            except json.JSONDecodeError:
                logger.warning("Failed to parse progress analysis, using default")
                state["progress_analysis"] = {
                    "health_status": "on_track",
                    "health_reason": "Project progressing as planned",
                    "key_accomplishments": [
                        f"Completed {req_summary['completed']} requirements"
                    ],
                    "progress_trend": "steady",
                    "concerns": [],
                    "next_milestones": ["Continue development"],
                }

        except Exception as e:
            logger.error(f"Error analyzing progress: {str(e)}", exc_info=True)
            state["error"] = f"Progress analysis error: {str(e)}"

        return state

    def _generate_subject(self, state: EmailGenerationState) -> EmailGenerationState:
        """Generate email subject line."""
        try:
            project_data = state["project_data"]
            analysis = state["progress_analysis"]
            req_summary = state["requirements_summary"]

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content="""You are creating an email subject line for a project progress update.
Create a professional, engaging subject line that:
1. Is concise (under 60 characters)
2. Mentions the project name
3. Highlights key progress metric or milestone
4. Creates curiosity without clickbait

Return ONLY the subject line text, no quotes or formatting."""
                    ),
                    HumanMessage(
                        content=f"""Project: {project_data['project_name']}
Completion: {req_summary['completion_percentage']}%
Health: {analysis['health_status']}
Key Achievement: {analysis['key_accomplishments'][0] if analysis['key_accomplishments'] else 'Progress update'}

Generate subject line:"""
                    ),
                ]
            )

            messages = prompt.format_messages()
            response = self.llm.invoke(messages)

            subject = str(response.content).strip().strip('"').strip("'")
            state["email_subject"] = subject

        except Exception as e:
            logger.error(f"Error generating subject: {str(e)}", exc_info=True)
            state["email_subject"] = (
                f"Project Update: {state['project_data']['project_name']}"
            )

        return state

    def _generate_body(self, state: EmailGenerationState) -> EmailGenerationState:
        """Generate plain text email body."""
        try:
            project_data = state["project_data"]
            client_data = state["client_data"]
            updates = state["recent_updates"]
            req_summary = state["requirements_summary"]
            analysis = state["progress_analysis"]

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content="""You are writing a professional project progress email to a client.
Write a warm, professional email that:
1. Greets the client by name
2. Provides clear progress summary
3. Highlights recent accomplishments
4. Addresses any concerns transparently
5. Outlines next steps
6. Maintains positive, confident tone
7. Ends with call to action or invitation for questions

Use proper email formatting with paragraphs and bullet points."""
                    ),
                    HumanMessage(
                        content=f"""Client Name: {client_data['client_name']}
Project: {project_data['project_name']}

Progress Summary:
- Completion: {req_summary['completion_percentage']}%
- Completed: {req_summary['completed']}/{req_summary['total']} requirements
- Status: {analysis['health_status']}

Key Accomplishments:
{chr(10).join(f"- {acc}" for acc in analysis['key_accomplishments'])}

Recent Updates:
{chr(10).join(f"- {upd['details']}" for upd in updates[:5])}

Concerns: {', '.join(analysis['concerns']) if analysis['concerns'] else 'None'}

Next Milestones:
{chr(10).join(f"- {ms}" for ms in analysis['next_milestones'])}

Write the email:"""
                    ),
                ]
            )

            messages = prompt.format_messages()
            response = self.llm.invoke(messages)

            state["email_body"] = str(response.content).strip()

        except Exception as e:
            logger.error(f"Error generating body: {str(e)}", exc_info=True)
            state["error"] = f"Email body generation error: {str(e)}"

        return state

    def _generate_html(self, state: EmailGenerationState) -> EmailGenerationState:
        """Generate HTML formatted email."""
        try:
            project_data = state["project_data"]
            client_data = state["client_data"]
            updates = state["recent_updates"]
            req_summary = state["requirements_summary"]
            analysis = state["progress_analysis"]

            health_colors = {
                "on_track": "#28a745",
                "at_risk": "#ffc107",
                "delayed": "#dc3545",
            }
            health_color = health_colors.get(
                analysis.get("health_status", "on_track"), "#28a745"
            )

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: -40px -40px 30px -40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #333;
        }}
        .progress-bar {{
            background-color: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 25px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .health-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            background-color: {health_color};
            color: white;
            font-weight: bold;
            margin: 10px 0;
        }}
        .update-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .accomplishment {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 12px;
            margin: 8px 0;
            border-radius: 5px;
        }}
        .milestone {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 8px 0;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Project Progress Update</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">{project_data['project_name']}</p>
        </div>
        
        <p class="greeting">Hello {client_data['client_name']},</p>
        
        <p>We're excited to share the latest progress on your project. Here's a comprehensive update on where we stand:</p>
        
        <div class="section">
            <h2>📈 Progress Overview</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {req_summary['completion_percentage']}%">
                    {req_summary['completion_percentage']}% Complete
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{req_summary['completed']}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{req_summary['in_progress']}</div>
                    <div class="stat-label">In Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{req_summary['pending']}</div>
                    <div class="stat-label">Pending</div>
                </div>
            </div>
            
            <p>
                <strong>Project Health:</strong>
                <span class="health-badge">{analysis['health_status'].replace('_', ' ').title()}</span>
            </p>
            <p>{analysis.get('health_reason', 'Project progressing as planned')}</p>
        </div>
        
        <div class="section">
            <h2>🎯 Key Accomplishments</h2>
"""

            for accomplishment in analysis.get("key_accomplishments", []):
                html += f'            <div class="accomplishment">✓ {accomplishment}</div>\n'

            html += """
        </div>
        
        <div class="section">
            <h2>📝 Recent Updates</h2>
"""

            for update in updates[:5]:
                html += (
                    f'            <div class="update-item">{update["details"]}</div>\n'
                )

            html += """
        </div>
        
        <div class="section">
            <h2>🚀 Next Steps</h2>
"""

            for milestone in analysis.get("next_milestones", []):
                html += f'            <div class="milestone">→ {milestone}</div>\n'

            if analysis.get("concerns"):
                html += """
        </div>
        
        <div class="section">
            <h2>⚠️ Points to Note</h2>
"""
                for concern in analysis["concerns"]:
                    html += f"            <p>• {concern}</p>\n"

            html += f"""
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <p style="font-size: 16px; margin-bottom: 15px;">We're here to answer any questions you may have.</p>
            <a href="mailto:support@example.com" class="cta-button">Contact Us</a>
        </div>
        
        <div class="footer">
            <p><strong>Thank you for your continued trust!</strong></p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            <p style="margin-top: 15px;">This is an automated progress report powered by AI.</p>
        </div>
    </div>
</body>
</html>
"""

            state["email_html"] = html

        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}", exc_info=True)
            state["error"] = f"HTML generation error: {str(e)}"

        return state

    def _save_email(self, state: EmailGenerationState, trigger_type: str) -> None:
        """Save the generated email to database."""
        try:
            update_ids = ",".join(
                str(upd["id"]) for upd in state["recent_updates"][:10]
            )

            email_record = ClientProgressEmail(
                project_id=state["project_id"],
                client_id=state["client_id"],
                trigger_type=trigger_type,
                subject=state["email_subject"],
                email_body_text=state["email_body"],
                email_body_html=state["email_html"],
                recipient_email=state["client_data"]["email"],
                delivery_status="sent",
                update_ids=update_ids,
                project_status=state["project_data"]["status"],
                sent_by=None,
            )

            self.session.add(email_record)
            self.session.commit()

            logger.info(f"Email record saved for project {state['project_id']}")

        except Exception as e:
            logger.error(f"Error saving email: {str(e)}", exc_info=True)
            self.session.rollback()


def get_pm_email_agent(session: Session) -> PMClientEmailAgent:
    """Factory function to create a PMClientEmailAgent instance."""
    return PMClientEmailAgent(session)
