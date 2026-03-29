# Cryptographic Failure Lab

This is a deliberately vulnerable Flask application demonstrating Cryptographic Failure vulnerabilities. This lab is part of the PyGoat project and contains three different scenarios.

## Vulnerabilities Demonstrated

1. Weak Hashing (e.g., MD5)
   - Uses weak, fast, and outdated hashing algorithms (MD5).
   - Hashes are easily crackable using precomputed hash tables (rainbow tables).
   - Demonstrates poor password protection practices.

2. Improved Hashing (But Still Crackable)
   - Uses slightly better but still fast hashing algorithm (SHA1).
   - Still vulnerable to brute-force attacks due to lack of salting or key stretching.
   - Emphasizes that even better hash algorithms without proper usage are weak.
   - Highlights importance of adaptive hashing.

1. Hardcoded Credentials 
   - Only non-admin credentials (User / P@$$w0rd) are provided.
   - Challenge is to escalate privileges or bypass auth to access admin-only data.

## Running the Lab

1. Build and run with Docker:
```bash
docker-compose up --build
```

2. Access the lab at http://localhost:5000

## Security Notice

This application contains intentional security vulnerabilities for educational purposes. DO NOT deploy this in a production environment or expose it to the public internet.
