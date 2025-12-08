# 🛠️ Backend Setup & Development Guide

## 1️⃣ Prerequisites & Installation

### Python Environment
1. **Create Virtual Environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR with uv
   uv install -r requirements.txt
   ```

3. **Environment Setup**:
   - Create a `.env` file in the `backend/` directory (copy from `.env-dev`).
   - Generate a secure `SECRET_KEY`:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Add it to your `.env` file.

## 2️⃣ Running the Application
Start the FastAPI server:
```bash
python main.py
```
- **API Documentation**: http://127.0.0.1:8000/docs
- My User Role Verification: `[POST] /api/login` (See docs)

---

## 3️⃣ PostgreSQL Database Setup
Follow these steps to set up the database correctly.

### 1. Database User Setup
Create a user in your system for postgres:
```bash
sudo -i -u postgres
``` 

### 2. Open Shell & Create Database
Open psql shell:
```bash
psql
```

Create database and user:
```sql
CREATE DATABASE se_preprod;
CREATE USER myuser WITH PASSWORD '12345678';
```

### 3. Grant Privileges
Run the following SQL block to ensure necessary permissions:
```sql
-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE se_preprod TO myuser;

-- Connect to the database first
\c se_preprod

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO myuser;
GRANT USAGE ON SCHEMA public TO myuser;
GRANT CREATE ON SCHEMA public TO myuser;

-- Make user owner of public schema (IMPORTANT!)
ALTER SCHEMA public OWNER TO myuser;

-- Grant all privileges on all tables, sequences, and functions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO myuser;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO myuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO myuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO myuser;
```

### 4. Update Configuration
Update `DATABASE_URL` in your `.env` file:
```plaintext
DATABASE_URL=postgresql://myuser:12345678@localhost/se_preprod
```

### Troubleshooting
**Permission Denied Error**:
If you get "permission denied for schema public", run as postgres superuser:
```sql
\c se_preprod
ALTER SCHEMA public OWNER TO myuser;
GRANT ALL ON SCHEMA public TO myuser;
```

---

## 4️⃣ Celery & Redis Setup (Async Tasks)
For background tasks (emails, reports, notifications), we use **Celery** with **Redis**.

### 1. Install Redis
- **Windows**: [Download installer](https://github.com/microsoftarchive/redis/releases)
- **macOS**: `brew install redis && brew services start redis`
- **Linux**: `sudo apt install redis-server && sudo systemctl start redis`

### 2. Configure Environment
Ensure your `.env` includes:
```ini
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Running Celery Services
Run these in separate terminals:

**Start Worker** (Processes background tasks):
```bash
celery -A app.celery_app worker --loglevel=info
```

**Start Beat Scheduler** (Triggers periodic tasks):
```bash
celery -A app.celery_app beat --loglevel=info
```

**Start Flower Dashboard** (Optional Monitoring):
```bash
celery -A app.celery_app flower --port=5555
```
> Monitor tasks at: http://localhost:5555

For more advanced configuration, see [CELERY_README.md](./CELERY_README.md).

---

## 5️⃣ MailHog Setup (Email Testing)
MailHog is an email testing tool for developers that captures all emails sent via SMTP and provides a web UI to view them.

### 1. Installation
- **Windows**: [Download from GitHub](https://github.com/mailhog/MailHog/releases)
- **macOS**: `brew install mailhog`
- **Linux**: 
  ```bash
  sudo wget -O /usr/local/bin/mailhog https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
  sudo chmod +x /usr/local/bin/mailhog
  ```
- **Docker**: `docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog`

### 2. Run MailHog
Start it from your terminal (or just run the executable on Windows):
```bash
mailhog
```
- **SMTP Server**: `localhost:1025`
- **Web UI**: http://localhost:8025

### 3. Configuration
Add these to your `.env` file:
```ini
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@syncem.com
```

For more details, see [MAILHOG_SETUP.md](./MAILHOG_SETUP.md).

---

## 6️⃣ Testing (Pytest)

### Run all tests
```bash
python3 -m pytest -vv
```

### Specific tests
```bash
# Run a specific folder
pytest tests/pm -vv

# Run a specific file
pytest tests/login/test_user_login.py -vv

# Run a specific function
pytest tests/test_user_login.py::test_post_admin_login -vv
```