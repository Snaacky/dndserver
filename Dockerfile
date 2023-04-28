# Choose a base Python image
FROM python:3.11.3-bullseye


# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Set the environment variable for Poetry to not create virtual environments
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy pyproject.toml and poetry.lock files
WORKDIR /app
# Copy the application's source code
COPY . .

# Expose the port your application will run on
EXPOSE 13337

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]