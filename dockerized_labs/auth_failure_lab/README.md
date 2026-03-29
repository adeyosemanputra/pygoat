# Identification and Authentication Failures Lab

This lab demonstrates OWASP Top 10 vulnerability Identification and Authentication Failures. 

## Vulnerabilities Demonstrated

1. Lab 1 - OTP Bypass:
   - Demonstrates lack of rate limiting in OTP verification
   - Vulnerable to brute force attacks
   - Contains hidden admin email in source code
   - Shows OTP for regular users but hides admin OTP

2. Lab 2 - Admin Panel:
   - Uses Argon2 for password hashing
   - Implements account lockout after 5 failed attempts
   - 24-hour lockout period
   - Tracks failed login attempts
   - Vulnerable to denial of service by locking out admin

3. Lab 3 - Session Management:
   - Uses UUID-based session tokens
   - Demonstrates session handling with database storage
   - Pre-configured users with SHA256 hashed passwords
   - Allows session invalidation/logout
   - Vulnerable to session fixation

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

4. Access the lab at http://localhost:5007

## Warning

This application contains intentional vulnerabilities for educational purposes. DO NOT deploy this in a production environment.
