# Security Policy

PyGoat is an **intentionally vulnerable** application for learning web
security. Most of what looks like a vulnerability in it is there on purpose,
so please read the scope below before reporting.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

Fixes land on the default branch and ship in the next 3.x release.

## Scope

**Out of scope (intended behaviour):** vulnerabilities inside the labs in
`dockerized_labs/` and `challenge/labs/`, and the deliberately insecure
examples in the lessons and solutions. These are the teaching material. If a
lab is *not* exploitable the way its lesson describes, open a normal issue.

**In scope:** problems in the PyGoat platform itself that would affect people
running it, for example:

- escaping a lab container to the host or to the Docker daemon
- reaching another user's lab or bypassing the Traefik `/auth/verify/` check
- account takeover or privilege escalation in the main Django app
  (login, registration, staff-only lab management)
- tampering with other users' scores or lab completions
- vulnerabilities in the install scripts, `Dockerfile` or `docker-compose.yml`
  that expose the host

## Reporting a Vulnerability

Please **do not open a public issue** for an in-scope vulnerability.

Report it privately through GitHub:
**Security → Report a vulnerability** on
<https://github.com/adeyosemanputra/pygoat/security>.

If that option is not available, open an issue titled "Security contact
request" **without any details**, and a maintainer will reach out to you
privately.

Please include:

- the PyGoat version or commit you tested
- how you run it (Docker Compose, from source, ...)
- steps to reproduce, and the impact you observed

## What to Expect

- **Acknowledgement:** within 7 days.
- **Assessment:** within 14 days we will confirm whether the report is in
  scope and share a fix plan.
- **Fix and disclosure:** we aim to release a fix within 90 days. We will
  coordinate the disclosure date with you and credit you in the release notes
  unless you prefer to stay anonymous.

PyGoat is maintained by volunteers, so timelines are best effort.
