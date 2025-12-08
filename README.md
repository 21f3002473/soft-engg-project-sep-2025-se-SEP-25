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
├── .github/
│   └── workflows/                # CI/CD pipelines
│
├── backend/                      # FastAPI backend + Celery + AI agents
│   ├── app/
│   │   ├── agents/               # GenAI agents (Employee, HR, PM)
│   │   ├── api/                  # API routes + validators
│   │   ├── controllers/          # Business logic
│   │   ├── core/                 # Core AI logic (PM agents)
│   │   ├── database/             # Models + DB connection
│   │   ├── middleware/           # Authentication + logging middleware
│   │   ├── services/             # Shared services
│   │   ├── static/               # Static files (docs, employee data)
│   │   ├── tasks/                # Celery background tasks
│   │   └── utils/                # Helper utilities
│   │
│   ├── tests/                    # Pytest suite
│   ├── images/
│   ├── Makefile
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── main.py
│
├── frontend/                     # Vue.js frontend
│   ├── public/                   # Static assets
│   ├── src/
│   │   ├── components/           # All Vue components grouped by role
│   │   ├── router/               # App routing
│   │   ├── store/                # Global state
│   │   ├── utils/                # Reusable utilities
│   │   └── assets/               # Images & brand assets
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env-dev
│
├── Client Meetings/              # Minutes of meetings with client
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

## 2️⃣ Install Dependencies & Configure
```
pip install -r requirements.txt
```
Create `.env` by copying sample from `.env-dev` in `backend/`.

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

#### Step 1: Inside psql, connected to postgres
Run the following inside the `psql` terminal:

```sql
CREATE DATABASE se_preprod;
CREATE USER myuser WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE se_preprod TO myuser;
```
#### Step 2: Switch to the new DB

```sql
\c se_preprod
```
#### Step 3: Now run schema + privilege commands

```sql
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

## 4️⃣ GenAI Setup (LLM & RAG)

### 1. Configure API Keys
Add your **Gemini** and **Groq** API keys to the `.env` file in `backend/`:
```ini
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

### 2. Build Vector Store (RAG)
Run the script to generate embeddings for the HR policy chatbot. 
Ensure you are in the `backend/` directory and your virtual environment is active.

```bash
# Windows
python app/agents/employee/rag/build_vector_store.py

# macOS / Linux
python3 app/agents/employee/rag/build_vector_store.py
```
> This generates `vectorstore.pkl` in `backend/app/static/employee/`.

---

## 5️⃣ Run the Backend
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
sudo docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
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
cd backend
source .venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

Beat:
```
cd backend
source .venv/bin/activate
celery -A app.celery_app beat --loglevel=info
```

Flower Dashboard:
```
cd backend
source .venv/bin/activate
celery -A app.celery_app flower --port=5555
```

Dashboard:
```
http://localhost:5555
```

---

## 6️⃣ Option: Using Makefile (Linux/macOS)
For Linux and macOS users, a `Makefile` is included in the `backend/` directory to simplify managing services like Redis, MailHog, and Celery.

**Available Commands:**
- `make help`      : Show available commands
- `make redis`     : Start Redis server
- `make mailhog`   : Start MailHog email server
- `make worker`    : Start Celery worker
- `make beat`      : Start Celery beat scheduler
- `make flower`    : Start Flower monitoring
- `make all`       : Start all services
- `make stop-all`  : Stop all services
- `make clean`     : Clean temporary files

To use it, simply navigate to the `backend/` directory and run the desired command (e.g., `make all`).

---

# 🎨 Frontend Setup

## 1️⃣ Install Dependencies
```
cd frontend
npm install
```

## 2️⃣ Configure API URL  
Create `.env` by copying sample from `.env-dev` in `frontend/`:

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
