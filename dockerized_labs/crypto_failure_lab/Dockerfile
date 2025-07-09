FROM python:3.9-slim

WORKDIR /app
COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install flask

EXPOSE 5000
CMD ["python", "app.py"]
