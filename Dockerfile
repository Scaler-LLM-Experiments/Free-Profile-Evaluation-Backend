FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies first to leverage Docker layer caching
COPY pyproject.toml uv.lock README.md /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

# Copy the application source
COPY . /app

EXPOSE 8000

ENV PORT=8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
