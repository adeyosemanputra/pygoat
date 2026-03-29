# -------- build stage --------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# hadolint ignore=DL3008
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

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps -w /wheels -r requirements.txt 


# -------- runtime stage --------
FROM python:3.11-slim-bookworm

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY . /app/

EXPOSE 8000

# v3 Healthcheck: Ensures Traefik knows when the backend is ready
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Performance: Using 6 workers as required by the Traefik ForwardAuth POC
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]