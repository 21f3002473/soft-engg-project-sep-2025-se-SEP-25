# Pytest Test Instructions

This project uses **pytest** for running backend tests.

## Prerequisites

### 1. Environment Configuration

Create a `.env` file inside the **backend** directory using the template from `.env-dev`.  
Fill in all required variables, including the email and password for roles.

To generate a secure `SECRET_KEY`, run:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Add the generated key to your `.env` file:

2. Set Up PostgreSQL

Follow the instructions in the backend README.md to:

Create and configure your PostgreSQL database

Set up users/roles

Apply migrations if needed
   
3. Ensure the backend server is running:
   
```bash
   python3 backend/main.py
```

4. Running Tests

To execute all tests with verbose output:
```bash
python3 -m pytest -vv
```