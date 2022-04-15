FROM python:latest

# set work directory
WORKDIR /app

# set environment variables
RUN apt -y update
RUN apt -y install dnsutils libpq-dev python3-dev
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . /app/

# install pygoat
RUN pip3 install /app
EXPOSE 8000

RUN python3 /app/pygoat/manage.py migrate
CMD ["python3", "pygoat/manage.py" ,"runserver", "0.0.0.0:8000"]
