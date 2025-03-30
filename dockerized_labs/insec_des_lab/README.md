# Insecure Deserialization Lab

A vulnerable web application demonstrating insecure deserialization vulnerabilities in Python using pickle.

## Description

This lab demonstrates the dangers of insecure deserialization by implementing a vulnerable user session mechanism that uses Python's pickle module. The application allows users to:

1. Create a regular user account
2. Receive a serialized token
3. Submit the token for deserialization
4. Exploit the vulnerability to gain admin access

## Features

- Vulnerable pickle deserialization
- Base64 encoded serialized data
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

## Lab Structure

```
insec_des_lab/
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker container definition
├── main.py             # Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static assets
│   └── style.css     # Theme and styling
└── templates/        # HTML templates
    ├── base.html    # Base template with theme support
    ├── index.html   # Main page
    └── result.html  # Results display
```

## Vulnerability Details

The lab uses Python's pickle module for serialization/deserialization of user data. The vulnerability exists because:

1. The application trusts user-provided serialized data
2. Uses pickle.loads() without validation
3. The User class has a vulnerable __reduce__ method

## Exploitation Steps

1. Create a regular user account
2. Intercept the serialized token
3. Decode the base64 token
4. Modify the serialized data to set is_admin=True
5. Re-encode the modified data
6. Submit the modified token to gain admin access

## Mitigation Strategies

To prevent insecure deserialization vulnerabilities:

1. Never use pickle for user-controlled data
2. Use secure serialization formats like JSON
3. Implement digital signatures for serialized data
4. Validate and sanitize all user input
5. Use principle of least privilege

