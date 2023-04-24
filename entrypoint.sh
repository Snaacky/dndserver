#!/bin/sh

# Entrypoint script for the D&D server
chmod +x /entrypoint.sh

# Install poetry
python -m pip install poetry

# Run poetry install
poetry install --only main --no-interaction --no-ansi

# Move to application directory
cd /app/dndserver

# Run Alembic upgrade
alembic upgrade head

# Move back to root directory
cd ..

# Start the server
python -m dndserver