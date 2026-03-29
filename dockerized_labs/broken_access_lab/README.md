# Broken Access Control Lab

A vulnerable web application demonstrating broken access control vulnerabilities in a Flask application.

## Description

This lab demonstrates broken access control vulnerabilities by implementing a vulnerable authentication system. The application allows users to:

1. Log in as a regular user (jack:jacktheripper)
2. Attempt to access admin content
3. Exploit the broken access control to gain admin privileges

## Features

- Vulnerable cookie-based access control
- User role system (regular user vs admin)
- Docker containerization
- Light/Dark theme support

## Security Warning

⚠️ This lab contains intentionally vulnerable code for educational purposes. Do not use this code in production environments.

## Installation

### Using Docker (Recommended)

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

2. Access the lab at http://localhost:8080

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
python main.py
```

## Vulnerability Details

The lab uses a simple cookie-based authentication system. The vulnerability exists because:

1. The application uses an easily modifiable cookie to determine admin status
2. No signature or encryption is used to protect the cookie
3. The application trusts the client-side cookie value without verification

## Exploitation Steps

1. Log in as the regular user (jack:jacktheripper)
2. Notice the 'admin' cookie is set to '0'
3. Use browser dev tools or an intercepting proxy to modify the cookie value to '1'
4. Access the page again to gain admin privileges

## Mitigation Strategies

To prevent broken access control vulnerabilities:

1. Implement proper session management
2. Use secure tokens (like JWT) for authorization
3. Implement proper access control checks
4. Never trust client-side data
5. Use the principle of least privilege
6. Log and monitor access control failures 