# Path Traversal Lab — A01 Broken Access Control

## Overview

This lab demonstrates a **path traversal** (directory traversal)
vulnerability, classified under
[OWASP A01:2025 – Broken Access Control](https://owasp.org/Top10/).

A file download endpoint constructs the file path by concatenating user
input directly to a base directory without any validation. An attacker
can inject `../` sequences to escape the intended folder, or supply an
absolute path such as `/etc/passwd`, and read arbitrary files on the
server.

## Running the Lab

In PyGoat v3 the sidebar launches a per-user container behind Traefik
(`start_lab` → host `<container>.<domain>`). For a standalone check:

```bash
docker compose up --build
```

The lab will be available at **http://localhost:5031**.
`GET /health` returns 200 so the v3 healthcheck can keep the container.

## Vulnerability

The `/download` endpoint in `app.py` is vulnerable:

```python
filepath = os.path.join(UPLOAD_DIR, filename)   # no validation
```

Because `filename` comes straight from the query string, a request like:

```
GET /download?file=../secret/admin_credentials.txt
```

resolves to the `secret/` directory outside of `uploads/`, leaking admin
credentials.

`os.path.join` also drops the base when the second part is absolute, so
`?file=/etc/passwd` reads that file without any `..` in the parameter.

## Exploitation

1. Open the lab and click any file to observe the URL pattern
   (`/download?file=<name>`).
2. Replace the filename with `../secret/admin_credentials.txt`.
3. The server returns the secret file contents including the flag.
4. Optionally try `?file=/etc/passwd` to see the absolute-path vector.

## Secure Fix

The `/download/secure` endpoint shows the correct approach:

```python
base = os.path.realpath(UPLOAD_DIR)
filepath = os.path.realpath(os.path.join(UPLOAD_DIR, filename))
if os.path.commonpath([base, filepath]) != base:
    abort(403)
```

`os.path.realpath()` resolves all `..` components and symlinks.
`os.path.commonpath` then requires the resolved path to stay inside the
uploads directory. A `startswith()` prefix check is not enough: it would
allow a sibling such as `/app/uploads_backup`.

## Port

**5031**
