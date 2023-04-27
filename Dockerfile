FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install poetry

RUN poetry install

EXPOSE 13337

CMD poetry run python -m dndserver.server