FROM python:3.11.0b1-buster

# Install dependencies
RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev=11.16-0+deb10u1 python3-dev=3.7.3-1 postgresql-client=11+200+deb10u4 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
 
# set work directory
RUN mkdir /opt/app
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --no-cache-dir pip==22.0.4
COPY ./requirements.txt /opt/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /opt/app/
