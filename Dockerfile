# pull the official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /pygoat/pygoat

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt /pygoat/pygoat
RUN pip install -r requirements.txt

# Requirements installation
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /
ENTRYPOINT ["entrypoint.sh"]
CMD ["python manage.py runserver"]