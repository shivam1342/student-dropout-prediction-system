FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application source.
COPY . .

# Railway injects PORT at runtime; default to 8080 for local container runs.
ENV PORT=8080

# Use a production WSGI server.
CMD ["sh", "-c", "gunicorn --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT} wsgi:app"]
