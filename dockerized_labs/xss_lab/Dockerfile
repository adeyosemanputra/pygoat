FROM python:3.9-alpine

WORKDIR /app


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 5006

# Command to run app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5006"]


