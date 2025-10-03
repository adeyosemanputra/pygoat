FROM python:3.10-slim-bullseye

# set work directory
WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    libffi-dev \
    libssl-dev \
    dnsutils \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip, setuptools, wheel
RUN python -m pip install --upgrade pip setuptools wheel

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Database migrations
RUN python3 /app/manage.py migrate

# Expose port
EXPOSE 8000

# Set working directory and start server
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
