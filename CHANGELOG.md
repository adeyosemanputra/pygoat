# Pygoat v3.0.0

Released 2026-10-21. This is the first stable release of PyGoat v3. The v2 codebase stays available on the `v2` branch.

## 1. Refactored Architecture

- All labs have been isolated as microservices using Docker.
- The labs implemented within Django were restructured into standalone Flask-based microservices. The in-app OWASP 2017 and 2021 labs were removed (#418, #426, #461).
- Integration is managed through a Django gateway orchestrated with Docker Compose.
- **Dynamic lab containers:** each user gets their own container per lab, started and stopped on demand, routed by Traefik at `lab-<user>-<lab>.<LAB_DOMAIN>` (#339). Containers are health-checked before use, and each user can run up to 3 labs at a time.
- **Per-user lab isolation:** Traefik ForwardAuth checks with Django that the logged-in user owns the lab before forwarding any request (#408).
- **Labs live in the database:** lab definitions and the sidebar menu are stored in the `Lab` and `LabCategoryMapping` models instead of a JSON file. Staff can add custom labs from the UI (#535).
- **Centralized UI:** the shared `common_lab.css` and layout components replace each lab's own copies (#539).

---

## 2. New Labs

### OWASP A03:2025 Software Supply Chain Failures
- **Dependency Attack Lab** (#330)
- **Package Injection Lab** (#331)
- **Open Source Library Attack Lab** (#332)

### Challenge Labs (#288)

#### a) Business Logic Flaw (Price Manipulation)
- **Scenario:** A shopping cart system allows applying discount codes.
- **Vulnerability:** Repeatedly applying the same coupon can reduce prices to almost zero.

#### b) Security Headers Misconfiguration
- **Scenario:** Application lacks critical headers such as `Content-Security-Policy (CSP)` and `X-Frame-Options`.
- **Vulnerability:** This enables **clickjacking** and **script injection** in certain contexts.

#### c) BoPLA — Broken Object Property Level Authorization
- **Scenario:** A profile update API allows direct manipulation of user attributes (e.g., `isAdmin=true`).
- **Vulnerability:** Due to insufficient validation of object properties, attackers can escalate privileges by tampering with hidden fields.

---

## 3. Scoring, Difficulty and Achievements (#541)

- Challenges and labs have a difficulty level (Easy, Medium, Hard, Expert) that multiplies their score.
- Scores also include a time bonus for fast solves.
- Achievements are awarded at completion milestones.
- A scoreboard dashboard and the user's score in the navbar.
- Challenge flags are submitted and checked on the server. Points are awarded only for a verified flag.

---

## 4. Secure Coding Showcase

- Added a **"Secure Fix" modal** within each lab.
- The modal includes:
  - Explanations of the secure patch.
  - OWASP-recommended best practices.
  - Solutions demonstrating how to fix the vulnerability.

---

## 5. Security Fixes

- Custom labs can only be created, edited or deleted by staff users. Build locations are restricted to `dockerized_labs/` and `challenge/labs/`. Previously any logged-in user could make the server build and run an image from any host path (#558).
- ForwardAuth does not trust client-supplied `X-Forwarded-Host` headers, and it checks lab ownership correctly for usernames that contain hyphens (#408).

---

## 6. Bug Fixes

- Sign-up no longer fails with a 500 error (#558).
- Challenges start and stop through the Docker SDK, so they work under Docker Compose. A challenge whose container died is restarted instead of reported as running (#558).
- The shared lab CSS loads in every lab under Docker Compose (#558).
- The three supply chain labs pass their health check and start (#558).
- A lab's first launch no longer times out while its image builds (#558).
- Failed lab containers no longer count toward the per-user lab limit. Parallel launches can no longer exceed it (#558).
- Lab image builds no longer leave intermediate containers behind (#558).
- `robots.txt` no longer returns a 500 error for anonymous users (#558).
- `wait_for_health()` no longer waits forever on containers without a health check (#513).
- Fixed the port availability check, which only worked on Linux (#504).
- The template injection lab's theme toggle works (#514).
- Fixed the light theme UI (#390).
- Fixed a missing return in the crypto failure view for anonymous users (#436).
- Fixed `os` variable shadowing in the command injection lab (#359).
- Replaced deprecated `datetime.utcnow()` (#357).
- Removed deprecated Django settings and added `DEFAULT_AUTO_FIELD` (#362, #363).
- Fixed spelling mistakes in `challenge/views.py` (#515).

---

## 7. Docker, CI and Project

- Multi-stage, hardened root Docker build on `python:3.11-slim-bookworm` (#392, #404). This also fixes the build failure caused by Debian Buster reaching end-of-life (#302).
- Standardized lab Dockerfiles and added `.dockerignore` files (#401, #417).
- Removed the deprecated `version` key from Compose files (#369).
- Modernized the flake8 and hadolint workflows (#399, #429, #430).
- Added PR and issue templates (#398), a pre-commit hook for formatting, and `KNOWN_ISSUES.md` (#318).

---

## Upgrade Notes

- v3 is meant to be run with Docker Compose (`docker compose up`). Open the app at <http://lvh.me:8000> so the login cookie is shared with lab subdomains.
- For a manual setup, run `python manage.py migrate`, then `seed_scoring`, `populate_labs` and `populate_challenges`.
- New settings, read from environment variables: `LAB_DOMAIN`, `LAB_COOKIE_DOMAIN` and `LAB_FORWARD_AUTH_URL`. `docker-compose.yml` sets them.
- Managing custom labs now requires a staff account.

## Known Issues

- The `do-it-fast` challenge image is amd64-only, so it does not start on ARM hosts such as Apple Silicon or Raspberry Pi without emulation.
- Most lab images use `python:3.9-alpine`, which has reached end-of-life.
- `DEBUG=True` is hard-coded on purpose because some labs rely on it. Do not expose PyGoat to the internet.

## Contributors

@ANIRUDH-SJ, @Garvita-k, @RogueBaker01, @RupakBiswas-2304, @caffeine-rohit, @mohityadav8, @samyak003, @saniyafatima07

---

# Pygoat v2.0.2 snapshot
### 1.Added
- **Custom Management Command:**  
  Added the `populate_challenges` command that reads challenge data from `challenge/challenge.json` and populates the `Challenge` table using `get_or_create` to prevent duplicate entries. The command handles missing files and JSON decode errors gracefully.
- Added `MIT License` to the project.

### 2.Changed
- **Challenge Model:**  
  - Updated the `save()` method to raise a `ValidationError` if `start_port` is greater than `end_port`.
  - Enhanced flag handling by hashing the `flag` field using SHA-256 (prefixed with "hashed_") if it hasn't been hashed already.

---

# Pygoat v2.0.1

1. New themes  
2. Bug fixing  

---

# PyGoat V2.0.0  

PyGoat Release Version 2.0.0  

* Whole new section for OWASP TOP 10 2021  
    i. New lab on template injection  
    ii. New 3 labs on cryptographic failure  
    iii. 1 more lab on broken access control  
    iv. 1 lab on Insecure Design  
    v. 1 more lab on security misconfiguration  
    vi. 1 new lab on using components with known vulnerability  
    vii. 2 new labs on Identification and Authentication failure  
    viii. 1 lab on software and data integrity failure and XXS  
    ix. Some labs on Insufficient logging  
    x. 2 new labs on SSRF  

* Section for Code discussion for most of the sections of OWASP 2021  

* Coding playground for SSRF  
        i. Authentication failure  
        ii. Insufficient logging  

* Added new section for SANS 25 and MITRE 25  

* Added new lab in SANS and MITRE 25 section  
    i. Path traversal  
    ii. Command injection  
    iii. Code injection  
    iv. CSRF  

* New Dark theme and improved UI  

* Better Docker file for smooth install  

* Brand new Logo  

---

# v2.0  

PyGoat Pre-Release Version 2.0  

* Whole new section for OWASP TOP 10 2021  
    i. New lab on template injection  
    ii. New 3 labs on cryptographic failure  
    iii. 1 more lab on broken access control  
    iv.
