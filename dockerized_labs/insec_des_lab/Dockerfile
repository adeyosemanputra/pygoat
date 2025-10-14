FROM python:3.12-slim@sha256:dc9e92fcdc085ad86dda976f4cfc58856dba33a438a16db37ff00151b285c8ca

WORKDIR /app

# ensure hash enforcement
ENV PIP_REQUIRE_HASHES=1

# copy the pinned+hashed lock file and install
COPY requirements.lab.txt ./requirements.lab.txt
RUN pip install --no-cache-dir --require-hashes -r requirements.lab.txt


COPY . .

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 8080

CMD ["flask", "run", "--debug", "--port=8080"]
