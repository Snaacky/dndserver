#!/bin/sh

# Entrypoint script for the D&D server
chmod +x ./entrypoint.sh

# Install poetry
python -m pip install poetry

# Run poetry install
python -m poetry install --no-dev --no-interaction --no-ansi

# Run Alembic upgrade
python -m alembic upgrade head

# Start the server
python -m dndserver.server