# Command Injection Lab

This lab demonstrates command injection vulnerabilities through two practical examples. It is part of the PyGoat project and has been converted to a standalone Flask application.

## Running the Lab

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. Access the lab at http://localhost:5013

## Lab Description

### Lab 1: Name Server Lookup
Demonstrates command injection through a DNS lookup feature:
- User inputs a domain name
- Application performs nslookup/dig command
- Vulnerable to command injection via shell metacharacters

Example payloads:
- `google.com && dir` (Windows)
- `google.com && ls` (Linux)
- `google.com; cat /etc/passwd` (Linux)

### Lab 2: Python eval()
Demonstrates code execution through Python's eval() function:
- User inputs a mathematical expression
- Application evaluates it using eval()
- Vulnerable to arbitrary Python code execution

Example payloads:
- `__import__('os').system('id')`
- `__import__('os').system('whoami')`

## Security Notes
This is a deliberately vulnerable application for educational purposes. Do not use any of these practices in production code.
