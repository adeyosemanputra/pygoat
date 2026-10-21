FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache bind-tools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5013

CMD ["python", "app.py"]
