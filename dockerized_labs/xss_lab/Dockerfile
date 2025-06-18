FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 5006

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Command to run app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5006"]


