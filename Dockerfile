FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    dnsutils \
    libpq-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r pygoat && useradd -r -g pygoat -d /app -s /usr/sbin/nologin pygoat

RUN chown pygoat:pygoat /app

COPY --chown=pygoat:pygoat . /app/

EXPOSE 8000

USER pygoat

RUN python3 /app/manage.py migrate

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]