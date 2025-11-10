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
CREATE DATABASE your_database_name;
```

4. create user 

```sql
CREATE USER your_username WITH PASSWORD 'your_password';

``` 

5. grant all privileges to the user on the database 

```sql
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
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
postgresql://your_username:your_password@localhost/your_database_name
```

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```bash
# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Add the generated key to your `.env` file:

