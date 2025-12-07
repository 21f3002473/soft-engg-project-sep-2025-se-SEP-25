# Celery Worker Setup

## Overview

This project uses Celery for asynchronous task processing with Redis as the message broker.

## Prerequisites

- Redis server installed and running
- Python dependencies installed (`uv sync` or `pip install -r requirements.txt`)

## Installation

### Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from https://github.com/microsoftarchive/redis/releases

### Install Python Dependencies

```bash
uv sync
# or
pip install celery redis flower
```

## Configuration

Add the following to your `.env` file:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running Services

### Option 1: Using Makefile (Recommended)

```bash
# Start all services
make all

# Or start individually
make redis        # Start Redis
make worker       # Start Celery worker
make beat         # Start Celery beat (scheduler)
make flower       # Start Flower monitoring

# Stop all services
make stop-all

# Clean temporary files
make clean
```

### Option 2: Using Shell Scripts

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

Start services:
```bash
# Start Redis
redis-server

# Start Celery worker
./scripts/start_worker.sh

# Start Celery beat (for scheduled tasks)
./scripts/start_beat.sh

# Start Flower (monitoring dashboard)
./scripts/start_flower.sh
```

### Option 3: Manual Commands

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Start Celery beat (optional, for scheduled tasks)
celery -A app.celery_app beat --loglevel=info

# Terminal 4: Start Flower (optional, for monitoring)
celery -A app.celery_app flower --port=5555
```

## Task Types

### Email Tasks (`app/tasks/email_tasks.py`)
- `send_email_task`: Send individual emails
- `send_welcome_email`: Welcome new users
- `send_password_reset_email`: Password reset emails

### Report Tasks (`app/tasks/report_tasks.py`)
- `generate_daily_report`: Daily system reports
- `generate_project_report`: Project-specific reports
- `export_data_to_csv`: Data export functionality

### Notification Tasks (`app/tasks/notification_tasks.py`)
- `send_notification`: Send notifications to users
- `cleanup_old_logs`: Clean up old system logs
- `process_batch_notifications`: Batch notification processing

## Using Tasks in Your Code

### Synchronous Execution
```python
from app.tasks.email_tasks import send_email_task

# This will block until complete
result = send_email_task("user@example.com", "Subject", "Body")
```

### Asynchronous Execution (Recommended)
```python
from app.tasks.email_tasks import send_email_task

# This returns immediately with a task ID
task = send_email_task.delay("user@example.com", "Subject", "Body")

# Check status later
if task.ready():
    result = task.result
```

### Scheduled Tasks
Scheduled tasks are defined in `app/celery_app.py`:
```python
celery_app.conf.beat_schedule = {
    "cleanup-old-logs-daily": {
        "task": "app.tasks.notification_tasks.cleanup_old_logs",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

## Monitoring

### Flower Dashboard
Access Flower at: http://localhost:5555

Features:
- Real-time task monitoring
- Worker status and statistics
- Task history and results
- Task retry and revoke

### CLI Monitoring
```bash
# Check worker status
celery -A app.celery_app status

# Inspect active tasks
celery -A app.celery_app inspect active

# View registered tasks
celery -A app.celery_app inspect registered

# Purge all tasks
celery -A app.celery_app purge
```

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A app.celery_app worker --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=998

[program:celery-beat]
command=/path/to/venv/bin/celery -A app.celery_app beat --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=999
```

### Using systemd

Create `/etc/systemd/system/celery-worker.service`:
```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A app.celery_app worker --detach
ExecStop=/path/to/venv/bin/celery -A app.celery_app control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
```

## Troubleshooting

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

### Worker Not Processing Tasks
```bash
# Check worker is running
celery -A app.celery_app inspect ping

# Check registered tasks
celery -A app.celery_app inspect registered

# Restart worker
make stop-all && make worker
```

### Task Failures
```bash
# View failed tasks
celery -A app.celery_app inspect failed

# Retry failed task
python
>>> from app.celery_app import celery_app
>>> celery_app.control.revoke('task-id', terminate=True)
```

## Best Practices

1. **Keep tasks idempotent**: Tasks should produce the same result if run multiple times
2. **Use timeouts**: Always set task time limits
3. **Handle failures gracefully**: Implement proper error handling and retries
4. **Monitor task performance**: Use Flower to identify bottlenecks
5. **Scale workers**: Add more workers for high-load scenarios
6. **Use task routing**: Route different task types to specific workers

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
