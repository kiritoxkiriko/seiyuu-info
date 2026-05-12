FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.8.0" \
    "uvicorn>=0.30.0"

COPY app ./app
COPY data ./data
COPY scripts ./scripts
COPY migrations ./migrations
COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md

EXPOSE 8787

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8787"]
