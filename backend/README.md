# Backend code

## how to run the app 

uv install -r requirements.txt

python3 main.py


API hit


use postgresql database 


![alt text](./images/image.png)

this is how you verify your role 


for fastapi documentation

http://127.0.0.1:8000/docs



## Setup postgres database for the app 


1. create a user in your system for postgres 

```bash
sudo -i -u postgres
``` 


2. open psql shell 

```bash
psql
```

3. create database 

```sql
CREATE DATABASE se_preprod;
```

4. create user 

```sql
CREATE USER myuser WITH PASSWORD '12345678';
``` 

5. grant all privileges to the user on the database 

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

6. exit psql shell 

```sql
\q
```

7. exit from postgres user 

```bash
exit
```

8. update the database connection string in your application configuration to use the created database and user credentials. The connection string format is usually like this:

```plaintext
postgresql://myuser:12345678@localhost/se_preprod
```

## Troubleshooting

### Permission Denied Error

If you get "permission denied for schema public", run these commands as postgres superuser:

```bash
sudo -i -u postgres
psql se_preprod
```

Then execute:

```sql
-- Make myuser the owner of the public schema
ALTER SCHEMA public OWNER TO myuser;

-- Grant all necessary privileges
GRANT ALL ON SCHEMA public TO myuser;
GRANT CREATE ON SCHEMA public TO myuser;

-- Exit
\q
exit
```

### Reset Database (if needed)

```bash
sudo -i -u postgres
psql
DROP DATABASE IF EXISTS se_pre_prod;
CREATE DATABASE se_pre_prod;
GRANT ALL PRIVILEGES ON DATABASE se_pre_prod TO myuser;
\c se_pre_prod
ALTER SCHEMA public OWNER TO myuser;
GRANT ALL ON SCHEMA public TO myuser;
\q
exit
```

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```bash
# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Add the generated key to your `.env` file:

## How to run Pytest

pytest tests/test_user_login.py
