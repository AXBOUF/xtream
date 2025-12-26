
---

PSQL QUICK NOTES [[RELATIONAL-DATABASE]]

WHAT PSQL IS  
psql = [[postgresql]] interactive shell  
Runs SQL + meta-commands  
Shell commands do NOT work here

---

BASIC NAVIGATION

\l  
List all databases

\c mydb  
Connect to database

\c mydb myuser  
Connect to database as specific user

\dt  
List tables in current database

\dt schema.*  
List tables in a schema

\d tablename  
Describe table structure

\du  
List users / roles

\q  
Exit psql

Meta-commands do not need semicolon

---

PROMPT MEANING

mydb=>  
Ready for SQL

mydb-#  
Waiting for command completion  
Usually missing semicolon or unclosed quote

Ctrl+C  
Cancel current input

---

SQL BASICS (REMEMBER SEMICOLON)

SELECT * FROM table;  
INSERT INTO table VALUES (...);  
CREATE TABLE name (...);  
DROP TABLE name;

No semicolon = Postgres waits forever

---

USER AND DATABASE MANAGEMENT

CREATE USER myuser WITH PASSWORD 'mypassword';  
Creates login role

CREATE DATABASE mydb OWNER myuser;  
Creates database owned by user

ALTER USER myuser CREATEDB;  
Give user permission to create DBs

DROP DATABASE mydb;  
Deletes database

DROP USER myuser;  
Deletes user

Run these as postgres or superuser

---

PERMISSIONS (COMMON)

GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;  
Allows user to fully access database

GRANT ALL ON ALL TABLES IN SCHEMA public TO myuser;  
Allows table access

Permissions issues are common in Docker setups

---

POSTGRES SUPERUSER ACCESS

sudo -iu postgres  
Switch to postgres OS user

psql  
Login as postgres superuser

Used mostly outside Docker or on servers

---

POSTGRES IN DOCKER (MENTAL MODEL)

Docker command runs OUTSIDE psql  
psql commands run INSIDE database

docker exec -it postgres-container psql -U user -d mydb  
Correct way to enter psql in container

docker compose exec db psql -U user -d mydb  
Same thing using docker-compose

Do NOT run docker commands inside psql

---

LOGIN METHODS

psql -U myuser -d mydb  
Local socket login

psql -U myuser -d mydb -h localhost  
TCP connection (used outside container)

Inside container, -h localhost usually unnecessary

---

COMMON DOCKER POSTGRES CHECKS

\l  
Confirm database exists

\du  
Confirm user exists

\c mydb myuser  
Confirm permissions

\dt  
Confirm tables visible

If any fail, it’s auth or ownership

---

PSQL HELP

?  
List all meta-commands

\h SELECT  
SQL help for a command

Good when you forget syntax

---

PYTHON CONNECTION CONTEXT

pip install psycopg2-binary  
Postgres adapter for Python

import psycopg2  
Used for ETL scripts and pipelines

Connection errors usually mean:  
Wrong host, port, user, password, or DB

---

MENTAL SHORTCUT (REMEMBER THIS)

Terminal  
→ Docker command  
→ psql shell  
→ SQL



