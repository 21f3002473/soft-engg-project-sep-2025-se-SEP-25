# 🎨 Frontend Setup & Development Guide

## 1️⃣ Prerequisites
- **Node.js**: v16+ (Recommended)
- **npm** or **yarn**
- **Backend**: Ensure the backend is running for full functionality (see `../backend/README.md`).

## 2️⃣ Installation

### 1. Install Dependencies
Navigate to the `frontend` directory and run:
```bash
npm install
```

### 2. Configure Environment
Create a `.env` file in the `frontend/` directory (copy from `.env-dev`):
```bash
# Example .env content
VUE_APP_API_URL=http://127.0.0.1:8000
```
> Update `VUE_APP_API_URL` if your backend is running on a different port/host.

## 3️⃣ Running the Application

### Start Development Server
Compiles and hot-reloads for development:
```bash
npm run serve
```
> App runs at: http://localhost:8080/

### Build for Production
Compiles and minifies for production:
```bash
npm run build
```

### Linting
Lints and fixes files:
```bash
npm run lint
```

---

## 4️⃣ Testing Credentials
Use these credentials to test different roles (if using seeded/predefined data):

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `root@example.com` | `supersecretpassword` |
| **Project Manager** | `pm@example.com` | `supersecretpassword` |
| **HR Manager** | `hr@example.com` | `supersecretpassword` |
| **Employee** | `employee@example.com` | `supersecretpassword` |