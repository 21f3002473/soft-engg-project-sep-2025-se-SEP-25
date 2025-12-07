# MailHog Setup Guide

## What is MailHog?

MailHog is an email testing tool for developers that:
- Captures all emails sent via SMTP
- Provides a web UI to view captured emails
- Doesn't send emails to real recipients (perfect for testing!)
- Supports email search, download, and release

## Installation

### macOS
```bash
brew update
brew install mailhog
```

### Linux (Ubuntu/Debian)
```bash
# Download latest release
sudo wget -O /usr/local/bin/mailhog https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64

# Make executable
sudo chmod +x /usr/local/bin/mailhog
```

### Windows
Download from: https://github.com/mailhog/MailHog/releases

### Docker (All platforms)
```bash
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

## Quick Start

### Start MailHog
```bash
# Using Makefile
make mailhog

# Or directly
mailhog

# Or using script
./scripts/start_mailhog.sh
```

### Configuration
MailHog runs on:
- **SMTP Server**: `localhost:1025` (for sending emails)
- **Web UI**: `http://localhost:8025` (for viewing emails)

### Environment Variables
Add to your `.env` file:
```env
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@projectmanagement.com
SMTP_FROM_NAME=Project Management System
MAILHOG_UI_URL=http://localhost:8025
```

## Testing Email Functionality

### 1. Start Services
```bash
# Terminal 1: Start Redis
make redis

# Terminal 2: Start MailHog
make mailhog

# Terminal 3: Start Celery Worker
make worker
```

### 2. Send Test Email via Python
```python
from app.tasks.email_tasks import send_welcome_email

# Send welcome email
task = send_welcome_email.delay(
    user_id=1,
    email="test@example.com",
    name="John Doe"
)

# Check task status
print(f"Task ID: {task.id}")
print(f"Task Status: {task.status}")
```

### 3. View Email in MailHog UI
Open browser to: http://localhost:8025

You should see:
- All captured emails
- Email preview (HTML and plain text)
- Email headers
- Download/Delete options

## Available Email Tasks

### Welcome Email
```python
from app.tasks.email_tasks import send_welcome_email

send_welcome_email.delay(
    user_id=123,
    email="user@example.com",
    name="John Doe"
)
```

### Password Reset Email
```python
from app.tasks.email_tasks import send_password_reset_email

send_password_reset_email.delay(
    email="user@example.com",
    reset_token="abc123token",
    user_name="John Doe"
)
```

### Project Assignment Email
```python
from app.tasks.email_tasks import send_project_assignment_email

send_project_assignment_email.delay(
    email="user@example.com",
    user_name="John Doe",
    project_name="Website Redesign",
    project_id="PRJ001"
)
```

### Requirement Update Email
```python
from app.tasks.email_tasks import send_requirement_update_email

send_requirement_update_email.delay(
    email="user@example.com",
    user_name="John Doe",
    requirement_id="REQ001",
    project_name="Website Redesign",
    status="COMPLETED"
)
```

## Integration Example

### In Your API Endpoint
```python
from app.tasks.email_tasks import send_welcome_email

@app.post("/api/admin/register")
def register_user(user_data: UserCreate):
    # Create user in database
    new_user = create_user(user_data)
    
    # Send welcome email asynchronously
    send_welcome_email.delay(
        user_id=new_user.id,
        email=new_user.email,
        name=new_user.name
    )
    
    return {"message": "User created", "user_id": new_user.id}
```

## MailHog Features

### Web UI Features
- **Search**: Find emails by recipient, subject, content
- **Download**: Download emails as .eml files
- **Delete**: Clear individual or all emails
- **Preview**: View HTML and plain text versions
- **Raw**: View raw MIME message

### API Endpoints
MailHog provides a REST API:

```bash
# Get all messages
curl http://localhost:8025/api/v2/messages

# Delete all messages
curl -X DELETE http://localhost:8025/api/v1/messages

# Get specific message
curl http://localhost:8025/api/v1/messages/{message_id}
```

## Troubleshooting

### MailHog not starting
```bash
# Check if port is already in use
lsof -i :1025
lsof -i :8025

# Kill existing process
pkill mailhog
```

### Emails not being captured
```bash
# Verify MailHog is running
ps aux | grep mailhog

# Check SMTP connection
telnet localhost 1025

# Check Celery worker logs
celery -A app.celery_app worker --loglevel=debug
```

### Cannot access Web UI
```bash
# Verify MailHog is listening on 8025
netstat -an | grep 8025

# Try accessing via
http://127.0.0.1:8025
```

## Production Considerations

**⚠️ Important**: MailHog is for **development/testing only**!

For production, use:
- **AWS SES** (Simple Email Service)
- **SendGrid**
- **Mailgun**
- **Postmark**
- **SMTP providers** (Gmail, Outlook, etc.)

### Switching to Production SMTP
Update `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

The email service will automatically use the configured SMTP server.

## Complete Workflow

```bash
# 1. Install MailHog
brew install mailhog  # macOS
# or download binary for other OS

# 2. Start all services
make all

# 3. Open MailHog UI
open http://localhost:8025

# 4. Trigger email from your app
# All emails will appear in MailHog UI

# 5. Stop all services
make stop-all
```

## Resources

- MailHog GitHub: https://github.com/mailhog/MailHog
- MailHog Documentation: https://github.com/mailhog/MailHog/blob/master/docs/README.md
- Alternative: Mailtrap (https://mailtrap.io/)
