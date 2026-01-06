FROM python:3.11-slim-bookworm

WORKDIR /app

# hadolint ignore=DL3008,DL3015
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        dnsutils \
        libpq-dev \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
