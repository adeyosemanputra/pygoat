FROM python:3.11.0b1-buster@sha256:97551b2b2d6af516fb98fe121d03b5877db165e493b0dd27bfae3b97c45cfcee


# set work directory
WORKDIR /app


# dependencies for psycopg2
RUN apt-get update && apt-get install --no-install-recommends -y dnsutils=1:9.11.5.P4+dfsg-5.1+deb10u11 libpq-dev=11.16-0+deb10u1 python3-dev=3.7.3-1 && apt-get clean && rm -rf /var/lib/apt/lists/*


# Runtime settings + enforce hash-checked pip installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_REQUIRE_HASHES=1


# --- Install Python deps (hashed) ---
# Copy the hashed lock file first to maximize layer cache
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --require-hashes -r requirements.txt


# copy project
COPY . /app/


# install pygoat
EXPOSE 8000


# RUN python3 /app/manage.py migrate
# WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
