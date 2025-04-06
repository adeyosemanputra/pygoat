# Use a lightweight official Python image
FROM python:3.11-slim

# Create a non-root user for better security
RUN useradd -m pygoatuser

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY app.py .

# Use the non-root user
USER pygoatuser

# Expose port Flask will run on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
