FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    EMBED_MODEL=BAAI/bge-small-en-v1.5 \
    EMBED_CACHE_DIR=/app/model_cache

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model at build time (cached in its own layer)
RUN python -c "import os; from fastembed import TextEmbedding; TextEmbedding(os.environ['EMBED_MODEL'], cache_dir=os.environ['EMBED_CACHE_DIR'])"

COPY src ./src

RUN useradd --uid 10001 --no-create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "ragapp.main:app", "--host", "0.0.0.0", "--port", "8000"]