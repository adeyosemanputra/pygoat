FROM python:latest

# set work directory
WORKDIR /app

# set environment variables
RUN apt-get update
RUN apt-get -y install dnsutils
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# copy project
COPY . /app/

# install pygoat
EXPOSE 8000

RUN python3 /app/pygoat/manage.py migrate
CMD ["python3", "pygoat/manage.py" ,"runserver", "0.0.0.0:8000"]
