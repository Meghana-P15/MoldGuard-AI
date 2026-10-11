# Build from repository root:
# docker build -f backend/Dockerfile -t moldguard-api .
FROM python:3.12-slim

WORKDIR /app

COPY ai/requirements.txt /tmp/ai-requirements.txt
COPY backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/ai-requirements.txt -r /tmp/backend-requirements.txt

COPY ai /app/ai
COPY backend /app/backend

ENV MODEL_DIR=/app/ai/models
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
