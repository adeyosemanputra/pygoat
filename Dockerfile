FROM python:3.11-slim-bookworm

# set work directory
WORKDIR /app

# dependencies for psycopg2
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    dnsutils \
    libpq-dev \
    python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies (keep cached when app code changes)
RUN python -m pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app/

EXPOSE 8000

# NOTE: run migrations at container start, not at build time
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]
