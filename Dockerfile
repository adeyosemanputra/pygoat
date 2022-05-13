FROM python:latest

# set work directory
WORKDIR /app

# set environment variables
RUN apt-get -y update
RUN apt-get -y install dnsutils
# dependencies for psycopg2
RUN apt-get -y install libpq-dev 
RUN apt-get -y install python3-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /app/

# install pygoat
EXPOSE 8000

RUN python3 /app/pygoat/manage.py migrate
WORKDIR /app/pygoat/
CMD ["gunicorn", "--bind" ,"0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
