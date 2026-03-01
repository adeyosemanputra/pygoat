# A02:2025 Cryptographic Failures Lab

Standalone dockerized lab demonstrating OWASP Top 10:2025 A02 - Cryptographic Failures vulnerabilities.

## Overview

This lab provides hands-on experience with 4 critical cryptographic failure scenarios:

### Scenario 1: Weak Encryption Algorithm
- Uses MD5 for password hashing (deprecated and easily crackable)
- Interactive registration and login system
- Rainbow table attack demonstration
- Admin password cracking challenge
- **Flag**: `FLAG{MD5_IS_BROKEN_USE_ARGON2}`

### Scenario 2: Insecure Cryptographic Storage
- Hardcoded encryption keys in source code
- Simulated leaked source code exposure
- Encrypted database dump
- Interactive decryption tool
- **Flag**: `FLAG{HARDCODED_KEYS_DESTROY_ENCRYPTION}`

### Scenario 3: Insufficient Randomness
- Weak PRNG (random.random()) with predictable time-based seeds
- Token prediction attack
- Admin token generated at known timestamp
- Demonstrates importance of secrets module
- **Flag**: `FLAG{PREDICTABLE_RANDOM_IS_NOT_RANDOM}`

### Scenario 4: CBC Bit-Flipping Attack
- AES-CBC encryption without HMAC integrity protection
- Cookie manipulation for privilege escalation
- XOR-based bit-flipping demonstration
- Shows need for authenticated encryption (AES-GCM)
- **Flag**: `FLAG{CBC_WITHOUT_MAC_ALLOWS_TAMPERING}`

## Running the Lab

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

Access at: http://localhost:5002

### Using Docker Only

```bash
docker build -t a02-crypto-failures .
docker run -p 5002:5002 a02-crypto-failures
```

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

## Educational Content

Each scenario includes:
- Detailed vulnerability explanation
- Real-world breach examples
- CWE mappings
- Vulnerable code examples
- Secure code alternatives
- Progressive hints for solving challenges
- Interactive labs with immediate feedback

## Security Notice

This application contains intentional security vulnerabilities for educational purposes only.

**DO NOT**:
- Deploy in production environments
- Expose to public internet
- Use any code patterns from this lab in real applications

## Technology Stack

- **Framework**: Flask 3.1.0
- **Cryptography**: pycryptodome 3.18.0, cryptography 39.0.1
- **Python**: 3.11

## License

Part of the PyGoat project - Educational security training platform
