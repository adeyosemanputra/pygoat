FROM python:3.11-slim

WORKDIR /app

COPY silent_privilege_escalation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# lab-specific
COPY silent_privilege_escalation/app.py .
COPY silent_privilege_escalation/templates ./templates

# shared assets
COPY shared/static ./static
COPY shared/templates ./shared_templates

EXPOSE 5000
CMD ["python", "app.py"]
