# Multi-Agent Research Orchestrator — Production Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Collect static files
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations and start Gunicorn server
CMD ["sh", "-c", "python manage.py migrate && gunicorn orchestrator_backend.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 4 --timeout 120"]
