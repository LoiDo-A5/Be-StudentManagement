FROM python:3.11
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade poetry
RUN pip install psycopg2-binary

WORKDIR /app

COPY pyproject.toml ./
COPY poetry.lock ./
COPY entrypoint.sh ./entrypoint.sh

RUN poetry install --no-root --only main

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
