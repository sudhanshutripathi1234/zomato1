FROM python:3.11-slim

WORKDIR /app

# System deps sometimes needed by pyarrow/pandas wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-api.txt

COPY data/restaurants.parquet data/restaurants.parquet
COPY src ./src
COPY .env.example .env.example

ENV PYTHONUNBUFFERED=1
ENV DATA_CACHE_PATH=data/restaurants.parquet

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
