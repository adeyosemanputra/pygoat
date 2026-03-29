# Compromised Open-Source Library Attacks Lab

This lab demonstrates how legitimate open-source packages can be compromised through repository takeovers, malicious updates, and supply chain attacks.

## Security Warning

⚠️ This lab contains intentionally vulnerable code for educational purposes. Do not use this code in production environments.

## Installation

### Using Docker (Recommended)

1. Build and run using Docker Compose:
docker-compose up --build

2. Access the lab at http://127.0.0.1:5022

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

1. Inject malicious logic into a previously legitimate package through a malicious update
2. Abuse maintainer takeover or repository access to distribute backdoored releases
3. Steal sensitive data while pretending to provide normal functionality
4. Spread malware through normal dependency update mechanisms
5. Exploit developer trust in popular open-source packages

## Mitigation Strategies

1. Version Pinning: Lock dependencies to known-good versions
2. Code Review: Review all dependency updates before installation
3. Maintainer Verification: Verify maintainer changes and ownership
4. Automated Scanning: Use tools to detect suspicious code patterns
5. Monitor Repositories: Watch for sudden changes in maintainers or code