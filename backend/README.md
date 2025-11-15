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
CREATE USER myuser WITH PASSWORD '12345678';

``` 

5. grant all privileges to the user on the database 

```sql
GRANT ALL PRIVILEGES ON DATABASE se_preprod TO myuser;
```
Also, you might want to set the ownership of the public schema to the created user:
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO myuser;
ALTER SCHEMA public OWNER TO myuser;
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

