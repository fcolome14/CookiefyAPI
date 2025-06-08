#!/bin/sh

echo ">> Waiting for DB..."
sleep 5  # Optional: give extra time before migration (depends_on helps but isn't perfect)

echo ">> Running migrations..."
alembic upgrade head

echo ">> Starting tests..."
pytest -vv
