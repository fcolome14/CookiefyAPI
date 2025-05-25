FROM python:3.10-slim

WORKDIR /code

# Install dependencies for PostgreSQL and build tools
RUN apt-get update && apt-get install -y gcc libpq-dev curl build-essential

# Install Poetry (using official method to avoid version issues)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Prevent Poetry from creating a virtualenv
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy lock and config files first to leverage Docker cache
COPY pyproject.toml poetry.lock* README.md ./

# Install only main/test dependencies
RUN poetry install --only main,test --no-interaction --no-root


# Copy the rest of the project
COPY . .

CMD ["pytest", "-v"]
