FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV SECRET_KEY="your_secret_key_here"
ENV JWT_SECRET_KEY="jwt_secret_key_here"

EXPOSE 5009

CMD ["python", "app.py"]
