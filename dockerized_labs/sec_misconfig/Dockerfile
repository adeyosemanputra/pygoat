FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
# Hard-coded secrets are intentional: this lab demonstrates security misconfiguration
# hadolint ignore=DL3064
ENV SECRET_KEY="your_secret_key_here"
# hadolint ignore=DL3064
ENV JWT_SECRET_KEY="jwt_secret_key_here"

EXPOSE 5009

CMD ["python", "app.py"]
