FROM python:3.11-slim

WORKDIR /app

# hadolint ignore=DL3008,DL3015
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        dnsutils \
        libpq-dev \
        python3-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --requirement requirements.txt

COPY . /app/

RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]
