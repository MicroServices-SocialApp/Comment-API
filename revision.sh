#!/bin/bash
set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Check if COMMENT_DATABASE_URL exists in .env
if ! grep -q "COMMENT_DATABASE_URL" .env; then
    echo "Error: COMMENT_DATABASE_URL not defined in .env"
    exit 1
fi

# Initialize Alembic directory if it doesn't exist
if [ ! -f "alembic.ini" ]; then
    echo "Alembic not initialized. Running 'alembic init --template async alembic' ..."
    alembic init --template async alembic
    echo "WARNING: Alembic initialized. You must now configure 'alembic/env.py' to load your DATABASE_URL and Models."
    exit 0 # Exit here so you can configure the file before running migrations
fi

# Generate the new migration
echo \n"Going to revision."\n
alembic revision --autogenerate -m "changed column name 'owner_id' to 'user_id'"

echo -e \n"Database revision complete."\n