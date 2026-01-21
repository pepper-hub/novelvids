# Backend Dockerfile
FROM python:3.12-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e ".[postgres]"

FROM base as development

# Install dev dependencies
RUN uv pip install --system -e ".[dev,postgres]"

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uvicorn", "novelvids.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base as production

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uvicorn", "novelvids.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
