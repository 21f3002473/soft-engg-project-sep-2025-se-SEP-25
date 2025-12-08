# Sync’em – AI-Powered Workforce & Project Management Platform

## ⭐ Overview
**Sync’em** is an AI-augmented workforce and project management platform built for **Admins**, **HR Managers**, **Project Managers**, and **Employees**.  
It provides role‑based dashboards, automated project allocation, AI chatbots, HR assistants, learning recommendations, background task automation, and complete workflow management.

Technologies used:
- **FastAPI**, **PostgreSQL**
- **Vue.js**, **TailwindCSS**
- **Celery**, **Redis**, **MailHog**
- **GenAI Agents (RAG + LLM-based assistants)**

---

# 📁 Project Structure
```
Syncem/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes (admin/hr/pm/employee)
│   │   ├── agents/              # GenAI chatbot, RAG modules
│   │   ├── controllers/         # Business logic layer
│   │   ├── database/            # Models + DB connection
│   │   ├── tasks/               # Celery tasks
│   │   ├── utils/
│   │   ├── middleware/
│   │   └── static/              # HR policy PDFs & assets
│   ├── tests/                   # Pytest suite
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Vue components
│   │   ├── router/
│   │   ├── store/
│   │   ├── utils/
│   │   └── App.vue
│   ├── public/
│   ├── .env                     # VUE_APP_API_URL lives here
│   ├── .env-dev
│   └── package.json
│
└── Milestones/ (All M1–M5 docs + code)
```

---

# ⚙️ Prerequisites

## Backend
- Python **3.10+**
- PostgreSQL **14+**
- Redis server
- Virtual environment tool

## Frontend
- Node.js **16+**
- npm or yarn

---

# 🛠 Backend Setup (Windows / macOS / Linux)

## 1️⃣ Create Virtual Environment
### Windows
```
cd backend
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

---

## 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```

---

## 3️⃣ PostgreSQL Installation & Setup
### 1. Install PostgreSQL

### **Ubuntu / Debian (Linux)**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Start and enable PostgreSQL:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### **macOS (Homebrew)**
```bash
brew update
brew install postgresql
brew services start postgresql
```

### **Windows**
Download the installer:  
https://www.postgresql.org/download/windows/

During installation:
- Set password for the **postgres** superuser  
- Install pgAdmin (optional GUI)

### 2. Entering the PostgreSQL Shell (`psql`)

### **Linux / macOS**
Switch to postgres user:
```bash
sudo -i -u postgres
```

Enter the shell:
```bash
psql
```

### **Windows**
Open **SQL Shell (psql)** from Start Menu  
or use **pgAdmin**.

### 3. Create Database, User & Permissions

Run the following inside the `psql` terminal:

```sql
CREATE DATABASE se_preprod;
CREATE USER myuser WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE se_preprod TO myuser;

-- Give ownership of schema
ALTER SCHEMA public OWNER TO myuser;

-- Allow usage + creation inside public schema
GRANT USAGE, CREATE ON SCHEMA public TO myuser;

-- Allow access to existing objects
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO myuser;

-- Ensure future objects also grant privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO myuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO myuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO myuser;
```

### 4. Exit psql
```sql
\q
```

### 5. Exit postgres system user (Linux/macOS)
```bash
exit
```

### 6. Update Your `.env` File

Add the database connection string:

```
DATABASE_URL=postgresql://myuser:12345678@localhost/se_preprod
```

---

## 4️⃣ Run the Backend
### Windows
```
.venv\Scripts\activate
python main.py
```

### macOS / Linux
```
source .venv/bin/activate
python3 main.py
```

Swagger documentation:
```
http://127.0.0.1:8000/docs
```

---

# 🎨 Frontend Setup

## 1️⃣ Install Dependencies
```
cd frontend
npm install
```

## 2️⃣ Configure API URL  
Create `.env` in `frontend/`:

```
VUE_APP_API_URL=http://127.0.0.1:8000
```

For production:
```
VUE_APP_API_URL=https://api.syncem.com
```

Restart the dev server after editing `.env`.

---

## 3️⃣ Start Frontend
```
npm run serve
```

Runs on:
```
http://localhost:8080/
```

### Local Test Accounts
```
root@example.com
pm@example.com
hr@example.com
employee@example.com
Password: supersecretpassword
```

---

# 📨 MailHog Setup (Email Testing)

## Install MailHog

### macOS
```
brew install mailhog
```

### Linux
```
sudo wget -O /usr/local/bin/mailhog https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
sudo chmod +x /usr/local/bin/mailhog
```

### Windows  
Download: https://github.com/mailhog/MailHog/releases

### Docker (any OS)
```
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

Start MailHog:
```
mailhog
```

Access UI:
```
http://localhost:8025
```

`.env`:
```
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@syncem.com
```

---

# ⚡ Celery Setup (Async + Scheduled Jobs)

## Install Redis

### macOS
```
brew install redis
brew services start redis
```

### Linux
```
sudo apt install redis-server
sudo systemctl start redis
```

### Windows  
Download redis package from Microsoft archive.

---

## Start Celery
Worker:
```
celery -A app.celery_app worker --loglevel=info
```

Beat:
```
celery -A app.celery_app beat --loglevel=info
```

Flower Dashboard:
```
celery -A app.celery_app flower --port=5555
```

Dashboard:
```
http://localhost:5555
```

---

# 🤖 Background Tasks
### Email Tasks
- Welcome email  
- Password reset  
- Project assignment  

### Report Tasks
- Daily reports  
- Project reports  
- CSV exports  

### Notifications
- Batch alerts  
- Cleanup jobs  

Example:
```python
send_welcome_email.delay(email="user@example.com", name="John")
```

---

# 📘 API Documentation
Full API docs:
```
http://127.0.0.1:8000/docs
```

Routes:
- `/api/admin`
- `/api/hr`
- `/api/employee`
- `/api/pm`

---

# 🧪 Testing (Pytest)
Run all tests:
```
pytest -vv
```

Run per module:
```
pytest tests/admin -vv
pytest tests/hr -vv
pytest tests/pm -vv
pytest tests/employee -vv
pytest tests/login -vv
```

---

# 🎯 Role-Based Features

## Admin
- System logs  
- Backups  
- User management  
- Updates  

## HR Manager
- Policies (CRUD)  
- Performance reviews (AI-assisted)  
- Employee management  
- HR chatbot  

## Project Manager
- Client requirements  
- Updates  
- Performance insights  
- AI assistant for requirement refinement  

## Employee
- Dashboard  
- Leave/Transfer/Reimbursement requests  
- Learning recommendations  
- Writing assistant  
- HR FAQ bot  

---

# 👨‍💻 Contributors
## 👥 Team 25 — IIT Madras (Software Engineering)
- Deon Levon Dmello
- Tummala Naveen
- Sayan Bhowmick
- Telvin Varghese
- Akbar Ali
- Sampriti Raha
- D Narendran 
- Soham Chakraborty

---

# 📄 License
Academic project under IIT Madras BS Degree (Software Engineering).
