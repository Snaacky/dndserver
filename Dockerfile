# Choose a base Python image
FROM python:3.11

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Set the environment variable for Poetry to not create virtual environments
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy pyproject.toml and poetry.lock files
WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY dndserver/alembic.ini ./
COPY config.yml dndserver/
COPY entrypoint.sh /entrypoint.sh
# Copy the application's source code
COPY . .

# Expose the port your application will run on
EXPOSE 30000

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]