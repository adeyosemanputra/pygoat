FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5020

CMD ["python", "app.py"]
