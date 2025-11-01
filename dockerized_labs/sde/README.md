# Sensitive Data Exposure (SDE) Lab

This lab demonstrates how sensitive data can be exposed when debug mode is enabled in production environments.

## Vulnerability Description

When Flask applications run with `DEBUG=True`, detailed error pages are shown that include:
- All configuration variables
- Environment variables  
- Stack traces with source code
- Local variables

## Lab Instructions

1. Start by accessing the main lab page at `/lab`
2. Try to find ways to trigger a 500 error
3. Look for clues in `/robots.txt` 
4. Access the `/500error` endpoint to trigger debug information
5. Find the `SENSITIVE_DATA` flag in the debug output

## Expected Learning Outcomes

- Understand how debug mode can expose sensitive information
- Learn about information disclosure vulnerabilities
- Recognize the importance of proper error handling in production

## Mitigation

- Never run applications with `DEBUG=True` in production
- Use proper logging instead of debug output
- Implement custom error pages that don't reveal sensitive information
- Be careful with configuration variable naming (avoid keywords like API, KEY, PASS, SECRET, SIGNATURE, TOKEN)

## How to Run

```bash
docker-compose up --build
```

Then access http://localhost:5100