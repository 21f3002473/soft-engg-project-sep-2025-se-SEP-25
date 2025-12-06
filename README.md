# Sync’em – AI-Powered Project & HR Assistance Platform

## Project Overview
Sync’em is an AI-driven workforce management system designed to help **HR Managers**, **Project Managers**, **Admins**, and **Employees** operate efficiently.  
It provides intelligent project allocation, HR‑policy chatbot responses, employee learning recommendations, performance reviews, and admin-level system controls.

The platform is built with:
- **FastAPI (Python)** for backend  
- **Vue.js** for frontend  
- **PostgreSQL** for database  
- **GenAI agents** integrated into multiple workflows  

---

## Project Team
- Akbar Ali  
- Deon Levon Dmello  
- D Narendran  
- Sampriti Raha  
- Sayan Bhowmick  
- Soham Chakraborty  
- Telvin Varghese  
- Tummala Naveen  

---

## Project Structure
```
Syncem/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routers
│   │   ├── controllers/     # Business logic
│   │   ├── database/        # Models + connection
│   │   ├── agents/          # GenAI RAG + chatbot
│   │   ├── middleware/
│   │   ├── utils/
│   │   └── static/docs/     # HR PDFs, assets
│   ├── tests/               # Pytest test cases
│   ├── requirements.txt
│   ├── config.py
│   └── main.py              # Entry point
│
├── frontend/                # Vue frontend
│   ├── public/
│   ├── src/
│   │   ├── components/      # UI components by role
│   │   ├── router/
│   │   ├── store/
│   │   ├── utils/
│   │   └── App.vue
│   ├── package.json
│   └── tailwind.config.js
|
├── .github/workflows/       # CI/CD pipelines
└── README.md
```

---

## Prerequisites

### Backend
- Python 3.10+
- PostgreSQL
- Virtual environment tool
- `.env` file with DB credentials + SECRET_KEY  

### Frontend
- Node.js v16+
- npm or yarn

---

## Backend Setup

### 1. Create Virtual Environment
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Configure PostgreSQL
Create DB + user:
```
CREATE DATABASE se_preprod;
CREATE USER myuser WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE se_preprod TO myuser;
```

Update your `.env`:
```
DATABASE_URL=postgresql://myuser:12345678@localhost/se_preprod
SECRET_KEY=your_generated_secret_key
```

### 4. Run the Backend
```
python3 main.py
```

Visit:
```
http://127.0.0.1:8000/docs   # Swagger UI
```

---

## Frontend Setup

### 1. Install Dependencies
```
cd frontend
npm install
```

### 2. Run Dev Server
```
npm run serve
```
Frontend runs at:
```
http://localhost:8080/
```

### Predefined Local Credentials (for development only)
```
ROOT_USER_EMAIL=root@example.com
PM_USER_EMAIL=pm@example.com
HR_USER_EMAIL=hr@example.com
EMPLOYEE_USER_EMAIL=employee@example.com
# all passwords: supersecretpassword
```

---

## Quickstart

### Start Backend
```
cd backend
source .venv/bin/activate
python3 main.py
```

### Start Frontend
```
cd frontend
npm run serve
```

---

## Key Features (Role‑Based)

### **Admin**
- Manage employees & roles  
- View logs  
- Monitor system status  
- Manage backups  
- Update system settings  

### **HR Manager**
- Manage employees  
- Manage HR policies  
- Generate performance reviews (GenAI-powered)  
- Chatbot for HR policies  
- Project overview + assignment  

### **Project Manager**
- Client requirements management  
- Automated client updates  
- Employee performance insights  
- AI assistant for requirement refinement  

### **Employee**
- Dashboard with tasks & announcements  
- Submit leave, transfer, reimbursement requests  
- Learning recommendations (GenAI)  
- Chatbot for HR queries  
- Notes + writing assistant  

---

## API Documentation
Full API documentation is available at:

```
http://127.0.0.1:8000/docs
```

Backend routes follow structured namespaces:
- `/api/admin`
- `/api/hr`
- `/api/employee`
- `/api/pm`

Swagger (Milestone 4) defines:
- Request/response schemas  
- Status codes  
- Auth flow (JWT)  

---

## Testing (Pytest)

### Run all tests
```
python3 -m pytest -vv
```

### Run tests per module
```
pytest tests/admin -vv
pytest tests/hr -vv
pytest tests/pm -vv
pytest tests/employee -vv
pytest tests/login -vv
```

Milestone 5 provides detailed expected vs. actual outputs, including failure scenarios (e.g., invalid JSON structure for reimbursement requests).

---

## Feature Walkthrough Summary

### 1. Authentication & Role-based Login
- Auto-redirect to role dashboards  
- JWT token validation  

### 2. Dashboards (for each role)
- HR: performance + allocation  
- PM: clients + updates + reports  
- Employee: tasks + requests + learning  

### 3. Chatbots (GenAI-powered)
- HR policy bot  
- Writing assistant  
- Employee guidance bot  

### 4. Project Allocation (AI-assisted)
- Matches employee skills, history & availability  

### 5. Requests System (Employee)
- Leave  
- Transfer  
- Reimbursement  
- Notes  

---

## Contributors
**Team 25 — September 2025 Batch**
- Akbar Ali  
- Deon Levon Dmello  
- D Narendran  
- Sampriti Raha  
- Sayan Bhowmick  
- Soham Chakraborty  
- Telvin Varghese  
- Tummala Naveen  

---

## License
This project is part of the **Software Engineering Course – IIT Madras Online Degree Program**.