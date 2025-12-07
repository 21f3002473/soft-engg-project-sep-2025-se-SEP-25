.PHONY: help redis worker beat flower mailhog stop-all clean

help:
	@echo "Available commands:"
	@echo "  make redis       - Start Redis server"
	@echo "  make mailhog     - Start MailHog email server"
	@echo "  make worker      - Start Celery worker"
	@echo "  make beat        - Start Celery beat scheduler"
	@echo "  make flower      - Start Flower monitoring"
	@echo "  make all         - Start all services"
	@echo "  make stop-all    - Stop all services"
	@echo "  make clean       - Clean temporary files"

redis:
	@echo "Starting Redis server..."
	redis-server --daemonize yes --port 6379

mailhog:
	@echo "Starting MailHog..."
	@mailhog > /tmp/mailhog.log 2>&1 &
	@echo "MailHog started!"
	@echo "SMTP: localhost:1025"
	@echo "Web UI: http://localhost:8025"

worker:
	@echo "Starting Celery worker..."
	celery -A app.celery_app worker --loglevel=info --concurrency=4

beat:
	@echo "Starting Celery beat..."
	celery -A app.celery_app beat --loglevel=info

flower:
	@echo "Starting Flower monitoring..."
	celery -A app.celery_app flower --port=5555

all: redis mailhog worker

stop-all:
	@echo "Stopping all services..."
	-pkill -f "celery worker"
	-pkill -f "celery beat"
	-pkill -f "celery flower"
	-pkill -f "mailhog"
	-redis-cli shutdown
	@echo "All services stopped."

clean:
	@echo "Cleaning temporary files..."
	rm -f /tmp/celerybeat.pid /tmp/celerybeat-schedule /tmp/mailhog.log
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete."
