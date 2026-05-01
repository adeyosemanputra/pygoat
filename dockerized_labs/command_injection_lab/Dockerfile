FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache bind-tools=9.20.22-r0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5013

CMD ["python", "app.py"]
