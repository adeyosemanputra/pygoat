FROM python:latest

# set work directory
WORKDIR /app

# set environment variables
RUN apt-get update
RUN apt-get -y install dnsutils
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /app/

EXPOSE 8000

CMD ["python3", "pygoat/manage.py" ,"runserver"]
