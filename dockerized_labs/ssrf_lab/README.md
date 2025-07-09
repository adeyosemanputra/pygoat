# SSRF Lab

This is a deliberately vulnerable Flask application demonstrating Server-Side Request Forgery (SSRF) vulnerabilities. This lab is part of the PyGoat project and contains two different SSRF scenarios.

## Vulnerabilities Demonstrated

1. File Reading SSRF
   - Path traversal vulnerability in file reading functionality
   - No input validation on file paths
   - Access to files outside intended directory

2. URL SSRF
   - No URL validation
   - Ability to access internal services
   - No restrictions on URL schemes or destinations


## Running the Lab

1. Build and run with Docker:
```bash
docker-compose up --build
```

2. Access the lab at http://localhost:5000

## Security Notice

This application contains intentional security vulnerabilities for educational purposes. DO NOT deploy this in a production environment or expose it to the public internet.
