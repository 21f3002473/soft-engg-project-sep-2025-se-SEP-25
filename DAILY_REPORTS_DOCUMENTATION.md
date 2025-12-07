# Daily Project Progress Report System - Documentation

## Overview
An automated AI-powered system that generates daily progress reports for projects using **LangChain** and **LangGraph**. The system analyzes project activity, identifies achievements and blockers, and sends comprehensive reports via email.

## System Architecture

### Backend Components

#### 1. Database Model (`ProjectDailyReport`)
**Location**: `backend/app/database/product_manager_models.py`

Stores all daily reports with:
- Report metadata (date, trigger type)
- AI-generated content (summary, achievements, blockers, upcoming tasks)
- Metrics (completion percentage, updates count)
- Email tracking (sent status, delivery status)

#### 2. LangGraph AI Agent (`PMDailyReportAgent`)
**Location**: `backend/app/core/agents/pm_agents/pm_daily_report_agent.py`

**7-Node Workflow**:
1. **fetch_data**: Retrieves project data, updates (last 24h), requirements, todos
2. **analyze_progress**: AI analysis of daily progress and trends
3. **generate_achievements**: Extracts key accomplishments from updates
4. **identify_blockers**: Identifies potential issues and concerns
5. **plan_upcoming**: Suggests focus areas for next 24 hours
6. **calculate_metrics**: Computes completion percentages and statistics
7. **generate_report**: Creates formatted text and HTML reports

**AI Model**: Groq API (llama-3.3-70b-versatile)
**Temperature**: 0.3 (for consistent, factual output)

#### 3. Celery Background Task (`generate_daily_project_report`)
**Location**: `backend/app/tasks/requirement_tasks.py`

- Runs asynchronously in background
- Can be scheduled for daily execution
- Generates report using AI agent
- Saves to database
- Sends email to client (if auto_send=True)

#### 4. REST API Endpoints
**Location**: `backend/app/api/resources/pm_resources/daily_reports.py`

**Routes**:
- `GET /api/pm/project/{project_id}/daily-reports` - List all reports
- `POST /api/pm/project/{project_id}/daily-reports` - Generate new report
- `GET /api/pm/daily-reports/{report_id}` - Get full report details

### Frontend Components

#### 1. Daily Reports Component (`ProjectDailyReports.vue`)
**Location**: `frontend/src/components/productmanager/fragments/ProjectDailyReports.vue`

**Features**:
- Lists all daily reports with summary cards
- Shows key metrics (updates count, completion %)
- Click to view full report in modal
- Generate new report button
- Pagination with "Load More"
- Email sent indicator
- Beautiful HTML report preview

#### 2. Project View Integration (`SingleProjectview.vue`)
**Location**: `frontend/src/components/productmanager/fragments/SingleProjectview.vue`

**Tab-Based Interface**:
1. **Requirements Tab**: Shows all project requirements
2. **Updates Tab**: Timeline of project updates
3. **Daily Reports Tab**: Daily progress reports component

## Report Content Structure

### Executive Summary
AI-generated 3-4 sentence overview of:
- Overall progress trend
- Velocity and momentum
- Concerns or risks
- Positive developments

### Key Achievements (Last 24 Hours)
- 3-5 concrete, measurable accomplishments
- Extracted from updates and completed tasks
- Example: "Completed user authentication module with OAuth integration"

### Blockers & Concerns
- 0-3 potential issues identified by AI
- Based on observable patterns:
  - Low update frequency
  - High pending/in-progress ratios
  - Status concerns
- Example: "Limited updates in last 24h may indicate blocked progress"

### Upcoming Focus Areas (Next 24 Hours)
- 3-5 prioritized tasks and focus areas
- Based on pending work and project status
- Actionable and realistic for 24-hour timeframe

### Project Metrics
- Updates (24h count)
- Requirements progress (completion %)
- Tasks progress (completion %)
- Overall completion percentage

## Automated Scheduling

### Setting Up Daily Report Generation

You can schedule reports using Celery Beat:

```python
# In backend/app/celery_app.py or beat_schedule configuration

from celery.schedules import crontab

app.conf.beat_schedule = {
    'generate-daily-reports': {
        'task': 'app.tasks.requirement_tasks.generate_daily_project_report',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
        'args': (project_id, client_id, True)  # auto_send=True
    },
}
```

### For Multiple Projects

Create a scheduled task that queries all active projects:

```python
@celery_app.task
def generate_reports_for_all_projects():
    """Generate daily reports for all active projects"""
    session = next(get_session())
    projects = session.exec(
        select(Project).where(Project.status == StatusTypeEnum.IN_PROGRESS)
    ).all()
    
    for project in projects:
        generate_daily_project_report.delay(
            project_id=project.id,
            client_id=project.client_id,
            auto_send=True
        )
```

## Email Notifications

When `auto_send=True`, the system:
1. Generates AI report
2. Retrieves client email
3. Sends formatted HTML email via Celery
4. Tracks delivery status
5. Records email_sent timestamp

## Usage Examples

### Manual Report Generation (Frontend)
1. Navigate to Project View
2. Click "Daily Reports" tab
3. Click "Generate Report" button
4. Report generates in background
5. View in list after ~10 seconds

### Manual Report Generation (API)
```javascript
POST /api/pm/project/123/daily-reports
{
  "auto_send": true
}
```

### View Report History
```javascript
GET /api/pm/project/123/daily-reports?limit=30&offset=0
```

### Get Full Report Details
```javascript
GET /api/pm/daily-reports/456
```

## Report HTML Template

The AI generates a beautifully formatted HTML report with:
- Gradient header with project info
- Color-coded sections:
  - 🟦 Executive Summary (blue)
  - 🟩 Achievements (green borders)
  - 🟨 Blockers (yellow borders)
  - 🟦 Upcoming Tasks (cyan borders)
- Metric cards with large numbers
- Responsive design
- Professional styling

## Key Features

### AI-Powered Analysis
- Intelligent progress assessment
- Pattern recognition in updates
- Automated achievement extraction
- Risk and blocker identification
- Smart task prioritization

### Automation
- Background processing with Celery
- Scheduled daily execution
- Automatic email delivery
- No manual intervention required

### History & Tracking
- All reports stored in database
- Searchable and filterable
- Email delivery tracking
- Completion metrics over time

### User Experience
- Clean tab-based interface
- One-click report generation
- Beautiful HTML previews
- Mobile-responsive design
- Real-time updates

## Database Migrations

To enable this feature, run:
```bash
cd backend
alembic revision --autogenerate -m "Add ProjectDailyReport model"
alembic upgrade head
```

## Dependencies

### Python Packages (Already Installed)
- langchain-core
- langchain-groq
- langgraph
- sqlmodel
- celery
- fastapi

### Environment Variables
```
GROQ_API_KEY=your_groq_api_key
```

## Testing

### Test Manual Generation
```bash
curl -X POST http://localhost:8000/api/pm/project/1/daily-reports?auto_send=true \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Scheduled Generation
```bash
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

## Monitoring

Check report generation status:
- View Celery logs for task execution
- Check database for new ProjectDailyReport entries
- Monitor email delivery status in report records
- Frontend shows generation progress with spinners

## Future Enhancements

1. **Trend Analysis**: Compare reports over time
2. **Alerts**: Notify PM if metrics decline
3. **Custom Schedules**: Per-project report timing
4. **PDF Export**: Download reports as PDF
5. **Chart Visualization**: Progress graphs in reports
6. **Slack Integration**: Send to Slack channels
7. **Custom Templates**: Configurable report formats

## Troubleshooting

### Reports Not Generating
- Check Celery worker is running
- Verify GROQ_API_KEY is set
- Check database connectivity
- Review logs for errors

### Emails Not Sending
- Verify email configuration in settings
- Check client email is valid
- Review email task logs
- Confirm SMTP settings

### AI Responses Empty
- Check GROQ API quota
- Verify API key is valid
- Review temperature settings
- Check LLM model availability

## Conclusion

This system provides **fully automated, AI-powered daily progress reporting** for projects with:
- ✅ LangChain/LangGraph AI workflows
- ✅ Automated email delivery
- ✅ Beautiful HTML reports
- ✅ Complete history tracking
- ✅ Tab-based UI integration
- ✅ Background processing
- ✅ Scheduled daily execution

The reports help project managers and clients stay informed about project progress without manual effort, using AI to intelligently analyze activity and generate actionable insights.
