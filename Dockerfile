FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y     dnsutils     libpq-dev     python3-dev     gcc     && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir pip==22.0.4
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN python3 manage.py migrate
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
