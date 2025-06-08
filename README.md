📖 **CookiefyAPI - FastAPI Social Media Project**
=================================================

Welcome to **CookiefyAPI**, a FastAPI-based social media project. This guide provides step-by-step instructions to set up the development environment using Poetry, connect to PostgreSQL, manage Alembic migrations, run the application, and execute integration tests using Docker.

* * * * *

✨ **Prerequisites**
-------------------

Before setting up the project, ensure the following tools are installed:

### 1. **Visual Studio Code (VS Code)**

-   Download: <https://code.visualstudio.com/>
-   Recommended Extensions:
    -   Python
    -   Pylance
    -   Docker (optional)

### 2. **Python (3.10 or higher)**

-   Download: <https://www.python.org/downloads/>
-   During installation on Windows, ensure "Add Python to PATH" is checked.

### 3. **Poetry**

-   Install:
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
-   Verify:
```
poetry --version
```

### 4. **PostgreSQL**

-   Download and install: <https://www.postgresql.org/download/>
-   Optionally install **pgAdmin**: <https://www.pgadmin.org/download/>

### 5. **Redis** (for Celery background tasks)

-   Quick local setup using Docker:
```
docker run -d -p 6379:6379 redis
```

* * * * *

🚀 **Table of Contents**
------------------------

1.  [Project Setup](#project-setup)
2.  [Environment Configuration](#environment-configuration)
3.  [Database Setup (PostgreSQL)](#database-setup-postgresql)
4.  [Poetry Environment & Dependency Management](#poetry-environment--dependency-management)
5.  [Alembic Migrations](#alembic-migrations)
6.  [Running the Application](#running-the-application)
7.  [Testing the API](#testing-the-api)
8.  [Docker-Based Testing](#docker-based-testing)
9.  [Common Issues & Troubleshooting](#common-issues--troubleshooting)
10. [Project Structure](#project-structure)
11. [Localization](#localization)
12. [Useful Commands](#useful-commands)

* * * * *

⚙️ **Project Setup**
--------------------

1.  **Clone the Repository:**
```
git clone https://github.com/your-username/cookiefyapi.git
cd cookiefyapi
```

2.  **Install Python (3.10+ recommended):**
```
python --version
```

* * * * *

🌍 **Environment Configuration**
--------------------------------

1.  **Create a `.env` file:**
```
cp .env.example .env
```

2.  **Edit `.env` with your values:**
```
# Project Info
PROJECT_NAME=Cookiefy
... (rest of your .env values)
```

* * * * *

📈 **Database Setup (PostgreSQL)**
----------------------------------

1.  **Install PostgreSQL:** <https://www.postgresql.org/download/>
2.  **Create user and database:**
```
psql -U postgres

CREATE USER fastapi_user WITH PASSWORD 'strongpassword';
CREATE DATABASE cookiefyapi_db OWNER fastapi_user;
GRANT ALL PRIVILEGES ON DATABASE cookiefyapi_db TO fastapi_user;
\q
```

* * * * *

📦 **Poetry Environment & Dependency Management**
-------------------------------------------------

1.  **Install Poetry:**
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

2.  **Set Python version (if needed):**
```
poetry env use python3.10
```

3.  **Install dependencies:**
```
poetry install
```

4.  **Find the virtualenv path (for VS Code):**
```
poetry env info --path
```

5.  **Set interpreter in VS Code** to the `python.exe` inside the path shown above.
6.  **Activate environment manually (optional):**
```
& "<venv_path>\Scripts\Activate.ps1"
```

* * * * *

⚒️ **Alembic Migrations**
-------------------------

1.  **Configure `alembic.ini`**:
```
sqlalchemy.url = postgresql://fastapi_user:strongpassword@localhost:5432/cookiefyapi_db
```

2.  **Generate migration:**
```
poetry run alembic revision --autogenerate -m "Initial migration"
```

3.  **Apply migration:**
```
poetry run alembic upgrade head
```

4.  **Check migration status:**
```
poetry run alembic current
```

5.  **Rollback (if needed):**
```
poetry run alembic downgrade -1
```

* * * * *

🚀 **Running the Application**
------------------------------

```
poetry run uvicorn app.main:app --reload
```
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

* * * * *

🔬 **Testing the API**
----------------------

1.  **Install test dependencies:**
```
poetry add --dev pytest httpx
```

2.  **Run tests:**
```
poetry run pytest
```

* * * * *

🐳 **Docker-Based Testing**
---------------------------

1. **Build and run integration tests using Docker Compose:**
```
docker-compose -f app/tests/compose/docker-compose.yml up --build
```

2. **Important Docker Notes:**
    - The `test` service in Docker uses a custom `entrypoint.sh` to:
        - Wait for PostgreSQL to be ready
        - Run Alembic migrations
        - Execute pytest
    - Make sure `entrypoint.sh` is executable:
      ```Dockerfile
      COPY app/tests/compose/entrypoint.sh /entrypoint.sh
      RUN chmod +x /entrypoint.sh
      ENTRYPOINT ["/entrypoint.sh"]
      ```
    - Alembic should point to the test DB inside the container (`cookiefy_test`).

3. **init.sql file (optional):**
    - If you want to pre-create multiple databases (e.g., `cookiefy`, `cookiefy_test`), your `init.sql` may look like:
      ```sql
      CREATE DATABASE cookiefy;
      CREATE DATABASE cookiefy_test;
      ```

* * * * *

❓ **Common Issues & Troubleshooting**
-------------------------------------

| Issue | Solution |
| --- | --- |
| `ModuleNotFoundError` | Run `poetry install` and select the correct interpreter in VS Code |
| `psycopg2.OperationalError` | Make sure PostgreSQL is running and `.env` is correct |
| `.env` not loading | Ensure `model_config = SettingsConfigDict(env_file=".env")` is in your `Settings` class |
| Alembic connection error | Check that your DB URL is valid and `.env` contains all required fields |
| Docker test DB not initialized | Check that Alembic migrations are run inside the container or via `entrypoint.sh` |

* * * * *

📁 **Project Structure**
------------------------

```
cookiefyapi/
├── app/
│   ├── api/             # API routes
│   ├── core/            # Settings, security
│   ├── db/              # DB session/init
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── tests/           # Tests
│   ├── main.py          # FastAPI entry point
│   └── dependencies.py
├── alembic/             # Alembic migrations
├── .env                 # Environment config
├── pyproject.toml       # Poetry config
├── README.md            # This file
├── Dockerfile           # Docker build config
└── app/tests/compose/   # Docker Compose test infra
```

* * * * *

📄 **Localization**
-------------------

```
# Extract messages
pybabel extract -F app/babel.cfg -o messages.pot .

# Initialize translations
pybabel init -i messages.pot -d app/locales -l en
pybabel init -i messages.pot -d app/locales -l es

# Update existing translations
pybabel update -i messages.pot -d app/locales

# Compile translations
pybabel compile -d app/locales
```

* * * * *

📜 **Useful Commands**
----------------------

| Task | Command |
| --- | --- |
| Install dependencies | `poetry install` |
| Add package | `poetry add <package>` |
| Remove package | `poetry remove <package>` |
| Run app | `poetry run uvicorn app.main:app --reload` |
| Create migration | `poetry run alembic revision --autogenerate -m "Message"` |
| Apply migrations | `poetry run alembic upgrade head` |
| Run tests | `poetry run pytest` |
| Run tests via Docker | `docker-compose -f app/tests/compose/docker-compose.yml up --build` |
| Enter Python shell | `poetry run python` |
| Show installed packages | `poetry show` |
| View venv path | `poetry env info --path` |

* * * * *

Happy hacking! 🤖
