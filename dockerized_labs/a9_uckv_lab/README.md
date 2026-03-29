# Using Components with Known Vulnerabilities Lab

This lab demonstrates OWASP Top 10 vulnerability A9: Using Components with Known Vulnerabilities. It showcases how using outdated libraries with known security issues can lead to serious security breaches.

## Vulnerabilities Demonstrated

1. PyYAML 5.1 Remote Code Execution
   - Vulnerable to code execution through YAML deserialization
   - CVE-2020-14343

2. Pillow 8.0.0 Command Injection
   - Vulnerable to command injection through image processing
   - Multiple CVEs related to image processing

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

4. Access the lab at http://localhost:9000

## Features

1. Lab 1: YAML Parsing
   - Demonstrates vulnerable YAML parsing
   - Shows version information
   - Allows file upload and parsing

2. Lab 2: Image Processing
   - Shows Pillow vulnerabilities
   - Allows image upload and processing
   - Demonstrates command injection

## Warning

This application contains intentional vulnerabilities for educational purposes. DO NOT deploy this in a production environment.
