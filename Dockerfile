FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential curl

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only the lock files first to leverage caching
COPY pyproject.toml poetry.lock ./

# Install only dependencies, not the current project
RUN poetry config virtualenvs.create false && \
    poetry install --with test --no-root --no-interaction

# Copy project source code
COPY . .

# Run tests
CMD ["pytest", "-v"]
