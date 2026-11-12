FROM python:3.12-slim-bookworm


# set work directory
WORKDIR /app


# dnsutils provides nslookup/dig, used by the cmd_lab feature
RUN apt-get update && apt-get install --no-install-recommends -y dnsutils && apt-get clean && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# copy project
COPY . /app/


RUN python3 /app/manage.py migrate

# Run as a dedicated non-root user, not root
RUN addgroup --system pygoat \
    && adduser --system --ingroup pygoat --home /app --no-create-home pygoat \
    && chown -R pygoat:pygoat /app
USER pygoat

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers","6", "pygoat.wsgi"]
