# Choose a base Python image
FROM python:3.11.3-slim-buster
LABEL maintainer="https://github.com/snaacky/dndserver"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Add Poetry path to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Install project dependencies with Poetry
COPY pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --only main --all-extras

# Place where the app lives in the container
WORKDIR /app
COPY . .

# Run database migrations
RUN alembic upgrade head

# Expose the port your application will run on
EXPOSE 13337

# Set the entrypoint
ENTRYPOINT ["python", "-m", "dndserver.server"]