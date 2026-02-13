FROM python:3.11-slim

# set work directory
WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dnsutils \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . .

EXPOSE 8000

# ❌ IMPORTANT: DO NOT RUN MIGRATIONS HERE
# migrations will be handled by docker-compose migration service

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]
