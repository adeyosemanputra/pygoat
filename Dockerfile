FROM python:3.11-slim

# set work directory
WORKDIR /app

# dependencies for psycopg2 and system libs
RUN apt-get update \
    && apt-get install --no-install-recommends -y dnsutils libpq-dev python3-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency file first
COPY requirements.txt requirements.txt

# Install Python dependencies (version pinning handled inside requirements.txt)
RUN pip install --no-cache-dir --requirement requirements.txt

# Copy project
COPY . /app/

# Apply migrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]
