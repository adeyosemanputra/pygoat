# Dependency Attack Lab

This lab demonstrates a dependency attack vulnerability in a Flask application.

## Security Warning

⚠️ This lab contains intentionally vulnerable code for educational purposes. Do not use this code in production environments.

## Installation

### Using Docker (Recommended)

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

2. Access the lab at http://127.0.0.1:5020

### Manual Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## Vulnerability Description

The lab contains a deliberately vulnerable application that demonstrates how malicious dependencies can:

1. Execute unauthorized code when imported
2. Exfiltrate sensitive data (API keys, credentials, configuration)
3. Operate silently without developer knowledge
4. Bypass security checks through trusted package names

## Mitigation Strategies

1. Verify Package Integrity: Use checksums and digital signatures
2. Dependency Scanning: Use tools like Snyk, OWASP Dependency-Check, pip-audit
3. Pin Versions: Lock dependency versions and review updates carefully
4. Verify Sources: Check package maintainers and repository authenticity
5. Least Privilege: Implement sandboxing and restrict what dependencies can access
6. Monitor Behavior: Log and alert on suspicious dependency activities