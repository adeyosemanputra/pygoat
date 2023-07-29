#ID=e3e38a1e-4a23-4d21-9ff5-03d0589517f5 python:3.11.0b1-buster 
FROM python:3.12.0b4-buster 

# set work directory
WORKDIR /app
#Adcionado um User para resolver a vulnerabilidade "ID:xxx"
USER MyUser 

# dependencies for psycopg2
RUN apt-get update && apt-get install --no-install-recommends -y dnsutils=1:9.11.5.P4+dfsg-5.1+deb10u7 libpq-dev=11.16-0+deb10u1 python3-dev=3.7.3-1 
\ && apt-get clean 
\ && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# copy project
COPY . /app/


# install pygoat
EXPOSE 8000


RUN python3 /app/manage.py migrate
WORKDIR /app/pygoat/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
