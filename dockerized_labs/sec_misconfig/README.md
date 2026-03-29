# Identification and Authentication Failures Lab

This lab demonstrates OWASP Top 10 vulnerability Security Misconfiguration. 

## Vulnerabilities Demonstrated

1. Lab 1: Header-based Authentication
   - Uses X-Host header for admin access
   - Must match "admin.localhost:8000" to get secret key
   
2. Lab 2: Debug Mode Exploitation
   - Debug=True setting exposes stack traces
   - Goal is to trigger a 500 error to access sensitive data

3. Lab 3: JWT Cookie Authentication
   - Uses JWT tokens for authentication
   - Cookie-based admin access

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose

### Running the Lab

1. Build and run the containers:
```bash
docker-compose up --build
```

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

4. Access the lab at http://localhost:5009

## Warning

This application contains intentional vulnerabilities for educational purposes. DO NOT deploy this in a production environment.
