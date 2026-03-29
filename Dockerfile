FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y dnsutils libpq-dev python3-dev gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]