FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential

# Copy the whole project (including README.md)
COPY . .

# Install poetry and dependencies
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --only main,test

CMD ["pytest", "-v"]
