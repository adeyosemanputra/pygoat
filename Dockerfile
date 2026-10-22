FROM python:3.11.0b1-buster


# set work directory
WORKDIR /app


# Debian buster is EOL; its packages were moved off the live mirrors to the
# permanent archive, so point apt there (and skip the now-expired Valid-Until check).
RUN sed -i 's|deb.debian.org/debian |archive.debian.org/debian |g; s|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until

# dnsutils provides nslookup/dig, used by the cmd_lab feature
RUN apt-get update && apt-get install --no-install-recommends -y dnsutils && apt-get clean && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install dependencies
RUN python -m pip install --no-cache-dir pip==22.0.4
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# copy project
COPY . /app/


# install pygoat
EXPOSE 8000


RUN python3 /app/manage.py migrate
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
