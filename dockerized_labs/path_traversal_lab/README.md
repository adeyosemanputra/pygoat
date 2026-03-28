# Path Traversal Lab — A01 Broken Access Control

## Overview

This lab demonstrates a **path traversal** (directory traversal) vulnerability, classified under [OWASP A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/).

A file download endpoint constructs the file path by concatenating user input directly to a base directory without any validation. An attacker can inject `../` sequences to escape the intended folder and read arbitrary files on the server.

## Running the Lab

```bash
docker-compose up --build
```

The lab will be available at **http://localhost:5031**.

## Vulnerability

The `/download` endpoint in `app.py` is vulnerable:

```python
filepath = os.path.join(UPLOAD_DIR, filename)   # no validation
```

Because `filename` comes straight from the query string, a request like:

```
GET /download?file=../secret/admin_credentials.txt
```

resolves to the `secret/` directory outside of `uploads/`, leaking admin credentials.

## Exploitation

1. Open the lab and click any file to observe the URL pattern (`/download?file=<name>`).
2. Replace the filename with `../secret/admin_credentials.txt`.
3. The server returns the secret file contents including the flag.

## Secure Fix

The `/download/secure` endpoint shows the correct approach:

```python
filepath = os.path.realpath(os.path.join(UPLOAD_DIR, filename))
if not filepath.startswith(os.path.realpath(UPLOAD_DIR)):
    abort(403)
```

`os.path.realpath()` resolves all `..` components and symlinks, and the `startswith()` check ensures the final path is still inside the allowed directory.

## Port

**5031** (as assigned in the project plan)
