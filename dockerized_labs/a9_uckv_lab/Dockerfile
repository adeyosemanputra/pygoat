FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential=12.9 \
    zlib1g-dev=1:1.2.13.dfsg-1 \
    libjpeg-dev=1:2.1.5-2 \
    libpng-dev=1.6.39-2+deb12u4 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 9000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "4", "app:app"]
