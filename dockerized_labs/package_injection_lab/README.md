# Package Injection / Typosquatting Lab

This lab demonstrates how typosquatting attacks work by tricking developers into installing malicious packages with similar names to popular libraries.

## Security Warning

⚠️ This lab contains intentionally vulnerable code for educational purposes. Do not use this code in production environments.

## Installation

### Using Docker (Recommended)

1. Build and run using Docker Compose:
docker-compose up --build

2. Access the lab at http://127.0.0.1:5021

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
1. The lab demonstrates a typosquatting attack where:
2. Developers accidentally install packages with typos (e.g., requets instead of requests)
3. Malicious packages execute code immediately upon import
4. Sensitive data is exfiltrated without developer knowledge
5. Backdoors are installed that can execute arbitrary commands
6. Package names look legitimate but are actually malicious

## Mitigation Strategies
1. Verify Package Names: Always double-check package names before installation
2. Use Requirements Files: Pin exact versions and review before installing
3. Package Verification Tools: Use tools like pip-audit, safety, or Snyk
4. Code Review: Review dependencies regularly and check for suspicious packages
5. Trusted Sources: Only install packages from verified maintainers
6. Automatic Scanning: Implement CI/CD checks that verify package names and scan for known typosquatting attacks
7. Read Package Docs: Check package documentation and GitHub repos before installing