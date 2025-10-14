FROM python:3.9-slim@sha256:aeebfa2890da7819f1617ec9a5650669570ab0802e5f51063aa8b7499da1ed26

WORKDIR /app

# ensure hash enforcement
ENV PIP_REQUIRE_HASHES=1

# copy the pinned+hashed lock file and install
COPY requirements.lab.txt ./requirements.lab.txt
RUN pip install --no-cache-dir --require-hashes -r requirements.lab.txt

COPY . .

# Add script to make sure migrations run properly
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
