# 📖 **CookiefyAPI - FastAPI Social Media Project**

Welcome to **CookiefyAPI**, a FastAPI-based social media project. This guide provides step-by-step instructions to set up the development environment, manage dependencies with Poetry, and run the application with PostgreSQL and Alembic.

---

## 🚀 **Table of Contents**
1. [Project Setup](#project-setup)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup (PostgreSQL)](#database-setup-postgresql)
4. [Poetry Commands](#poetry-commands)
5. [Alembic Migrations](#alembic-migrations)
6. [Running the Application](#running-the-application)
7. [Testing the API](#testing-the-api)
8. [Common Issues & Troubleshooting](#common-issues--troubleshooting)
9. [Project Structure](#project-structure)
10. [Language](#language)

---

## ⚙️ **Project Setup**

1. **Clone the Repository:**

```bash
git clone https://github.com/your-username/cookiefyapi.git
cd cookiefyapi
```

2. **Install Python (3.10+ recommended):**

```bash
python --version
```

## 🌍 Environment Configuration

1. Create a .env file:
 
```bash
cp .env.example .env
```

````.env```` Example:

```bash
# Database Configuration
DATABASE_URL=postgresql://<fastapi_user>:<strongpassword>@localhost:5432/cookiefyapi_db

# Security Settings
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

2. Update the ````.env```` file with your database credentials and app settings.

## 🗄️ Database Setup (PostgreSQL)

1. Install PostgreSQL: <br>
[Download here](https://www.postgresql.org/download/)

2. Create Database and User: <br>
Log into PostgreSQL: <br>

```bash
psql -U postgres
```

Run the following commands:

```bash
-- Create user and database
CREATE USER <fastapi_user> WITH PASSWORD '<strongpassword>';
CREATE DATABASE cookiefyapi_db OWNER fastapi_user;
GRANT ALL PRIVILEGES ON DATABASE cookiefyapi_db TO <fastapi_user>;
```
Exit ````psql````:

```bash
\q
```

## 📦 Poetry Commands

1. Install Poetry (if not already installed): <br>

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or if using powershell terminal:

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```


2. Set Up Virtual Environment: <br>

```bash
poetry env use python3.10
```

3. Install Project Dependencies: <br>

```bash
poetry install
```

4. Activate Virtual Environment: <br>

```bash
poetry env activate
```

5. Check Installed Packages:: <br>

```bash
poetry show
```

## ⚒️ Alembic Migrations

1. Initialize Alembic (First Time Only): <br>

```bash
poetry run alembic init alembic
```

2. Configure Database in ````alembic.ini````: <br>

```bash
sqlalchemy.url = postgresql://<fastapi_user>:<strongpassword>@localhost:5432/cookiefyapi_db
```

3. Generate Migrations: <br>

```bash
poetry run alembic revision --autogenerate -m "Initial migration"
```

4. Apply Migrations: <br>

```bash
poetry run alembic upgrade head
```

5. Check Current Migration: <br>

```bash
poetry run alembic current
```

6. Rollback Migration (If Needed): <br>

```bash
poetry run alembic downgrade -1
```

## 🚀 Running the Application

1. Start FastAPI with Uvicorn: <br>

```bash
poetry run uvicorn app.main:app --reload
```

2. API Documentation: <br>

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

3. Stop the Server: <br>

Press ````CTRL + C```` to stop the server.


## 🔬 Testing the API

1. Install Testing Dependencies: <br>

```bash
poetry add --dev pytest httpx
```

2. Run Tests: <br>

```bash
poetry run pytest
```

## ❓ Common Issues & Troubleshooting

1. Database Connection Error (psycopg2.OperationalError): <br>

- Ensure PostgreSQL is running:

```bash
sudo systemctl start postgresql  # Linux/macOS
net start postgresql             # Windows
```

-Test connection:

```bash
psql -U <fastapi_user> -d cookiefyapi_db
```

2. Package Not Found (````ModuleNotFoundError````):
- Ensure you're in the Poetry virtual environment:

```bash
poetry shell
```

## 📁 **Project Structure**

```bash
cookiefyapi/
├── app/
│   ├── api/             # API routes (endpoints)
│   ├── core/            # Core settings and security
│   ├── db/              # Database connection
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── tests/           # Test files
│   ├── main.py          # Application entry point
│   └── dependencies.py  # Common dependencies
├── alembic/             # Database migrations
├── .env                 # Environment variables
├── pyproject.toml       # Poetry configuration
├── README.md            # Project documentation
└── Dockerfile           # Container setup (optional)
```

## **Language**

To compile ````babel.cfg```` run:

```bash
pybabel extract -F app/babel.cfg -o messages.pot .
```

To initialize new translations a ````.po```` file run:

```bash
pybabel init -i messages.pot -d app/locales -l en
pybabel init -i messages.pot -d app/locales -l es
```

To update existing translations run:

```bash
pybabel update -i messages.pot -d app/locales
```

Compile them from a ````.po```` into binary ````.mo```` file by running:

```bash
pybabel compile -d app/locales
```

## 📜 **Useful Commands**

| **Task**                | **Command**                                          |
|--------------------------|-------------------------------------------------------|
| Install dependencies     | `poetry install`                                      |
| Add a package            | `poetry add <package>`                                |
| Remove a package         | `poetry remove <package>`                             |
| Run app                  | `poetry run uvicorn app.main:app --reload`            |
| Create Alembic migration | `poetry run alembic revision --autogenerate -m "Message"` |
| Apply migrations         | `poetry run alembic upgrade head`                     |
| Run tests                | `poetry run pytest`                                   |
