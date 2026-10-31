FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies. PIP_CONSTRAINT also applies to the isolated
# build environments pip uses for the source builds, so setuptools stays pinned.
COPY requirements.txt build-constraints.txt ./
RUN PIP_CONSTRAINT=build-constraints.txt pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 9000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "4", "app:app"]
