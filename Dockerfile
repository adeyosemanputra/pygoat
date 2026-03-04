# Build stage
FROM docker.io/library/python:3.11.14-alpine3.23 AS builder

# Dependencies for building psycopg2
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev

# Setup dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Run stage
FROM docker.io/library/python:3.11.14-alpine3.23 AS runtime

# Install runtime dependencies
RUN apk add --no-cache libpq

# Working directory on the container
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Set PATH to include the local bin directory where pip installs packages
ENV PATH=/root/.local/bin:$PATH

# Copy the application code
COPY . /app/

# Set environment variables specific for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Port the application will run on
EXPOSE 8000

# Run the application using Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 --workers 6 pygoat.wsgi"]
