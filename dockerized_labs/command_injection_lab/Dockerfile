FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y dnsutils && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r requirements.txt

COPY . .

EXPOSE 5013

CMD ["python", "app.py"]
