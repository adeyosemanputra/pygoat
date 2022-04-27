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

# copy project
COPY . /app/

# Install requirements
RUN pip install -r /app/requirements.txt

# install pygoat
EXPOSE 8000

RUN python3 /app/pygoat/manage.py migrate
CMD ["python3", "pygoat/manage.py" ,"runserver", "0.0.0.0:8000"]
