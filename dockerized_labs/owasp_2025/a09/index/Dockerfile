FROM python:3.11-slim

WORKDIR /app

COPY index/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# lab-specific
COPY index/app.py .
COPY index/templates ./templates

# shared assets
COPY shared/static ./static
COPY shared/templates ./shared_templates

EXPOSE 5000
CMD ["python", "app.py"]
