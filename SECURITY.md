# 🛡️ Security Policy — PyGoat

> PyGoat is an **intentionally vulnerable** Django web application maintained by OWASP,  
> designed to teach real-world web security through hands-on labs.  
> This policy covers **infrastructure security** — not the intentional lab vulnerabilities.

---

## 📦 Supported Versions

Only the latest version of PyGoat receives security maintenance.  
Older branches are unsupported and should not be used in any environment beyond local isolated testing.

| Version  | Supported          | Notes                              |
|----------|--------------------|-------------------------------------|
| `latest` | ✅ Active           | Receives patches and updates        |
| `older`  | ❌ Unsupported      | Use at your own risk                |

---

## ⚠️ Important Disclaimer — This App Is Intentionally Broken

PyGoat ships with **real, working vulnerabilities** as part of its curriculum. These include:

| Lab Category             | OWASP / MITRE Reference                     | Status         |
|--------------------------|---------------------------------------------|----------------|
| SQL Injection            | OWASP A03:2021 — Injection                  | ✅ Intentional  |
| XSS (Stored/Reflected)   | OWASP A03:2021 — Injection                  | ✅ Intentional  |
| Broken Access Control    | OWASP A01:2021 — Broken Access Control      | ✅ Intentional  |
| Broken Authentication    | OWASP A07:2021 — Identification & Auth Fail | ✅ Intentional  |
| Cryptographic Failures   | OWASP A02:2021 — Cryptographic Failures     | ✅ Intentional  |
| SSRF                     | OWASP A10:2021 — SSRF                       | ✅ Intentional  |
| XXE Injection            | OWASP A05:2021 — Security Misconfiguration  | ✅ Intentional  |
| SSTI                     | OWASP A03:2021 — Injection                  | ✅ Intentional  |
| Insecure Deserialization | OWASP A08:2021 — Software Integrity Failure | ✅ Intentional  |
| Command Injection        | MITRE CWE-78                                | ✅ Intentional  |
| CSRF                     | MITRE CWE-352                               | ✅ Intentional  |
| Sensitive Data Exposure  | OWASP A02:2021                              | ✅ Intentional  |
| Security Misconfiguration| OWASP A05:2021                              | ✅ Intentional  |

> **Do NOT report these as vulnerabilities.** They are the entire point of the project.

---

## 🚨 What TO Report

Please report issues that affect **PyGoat's own infrastructure** — things that are broken *unintentionally* and outside the scope of the learning labs:

### ✅ In Scope

- **Authentication bypass of the Django admin panel** (`/admin/`) that is not part of any lab exercise
- **Remote Code Execution** that escapes the intended lab sandbox
- **Privilege escalation** between user accounts not covered by any lab
- **Docker container escape** from any of the dockerized labs:
  - `broken_auth_lab`
  - `insec_des_lab`
  - `sensitive_data_exposure`
- **Dependency vulnerabilities** with a direct exploit path affecting PyGoat's own runtime (Django 4.2, PyJWT 2.4.0, Pillow 9.4.0, cryptography 39.0.1, etc.)
- **Unintended secret/token exposure** in source code, logs, or HTTP responses — outside of what labs intentionally expose
- **CI/CD pipeline vulnerabilities** (`.github/workflows/flake8.yml`, `hadolint.yml`)

### ❌ Out of Scope

- Any lab vulnerability listed in the table above
- Vulnerabilities already documented in `/Solutions/solution.md`
- The hardcoded `SECRET_KEY` and `DEBUG = True` in `pygoat/settings.py` — these are intentional for local lab use
- The `SECRET_COOKIE_KEY = "PYGOAT"` setting — intentional for lab exercises
- Vulnerabilities in third-party packages — report those directly to the package maintainer
- Issues only reproducible in production deployments (PyGoat is not meant to be deployed publicly)

---

## 📬 How to Report

**Do NOT open a public GitHub issue.** Doing so exposes the vulnerability before it can be fixed.

Instead, send a detailed email to:

📧 **owasp-pygoat@owasp.org**

### What to Include in Your Report

```
Subject: [PyGoat Security] <Brief one-line description>

1. Vulnerability Type
   e.g. Privilege Escalation, Container Escape, RCE

2. Affected Component
   e.g. /introduction/views.py, docker-compose.yml, challenge/views.py

3. Environment
   - PyGoat version / commit hash
   - Python version
   - Django version
   - OS / Docker version (if applicable)

4. Steps to Reproduce
   Provide clear, numbered steps from a fresh install.

5. Proof of Concept
   Include code snippets, curl commands, or screenshots.

6. Impact Assessment
   What can an attacker achieve? Data access? Shell access?

7. Suggested Fix (optional but appreciated)
```

---

## ⏱️ Response Timeline

| Action                         | Target Timeframe |
|--------------------------------|------------------|
| 📨 Initial acknowledgement      | Within 48 hours  |
| 🔍 Triage and status update     | Within 7 days    |
| 🛠️ Fix or decision communicated | Within 30 days   |
| 📢 Public disclosure (if fixed) | Coordinated with reporter |

---

## 🔐 Deployment Security Warning

PyGoat is a **deliberately insecure application**. Running it outside of an isolated local environment is dangerous and irresponsible. The following settings are intentionally misconfigured for lab purposes and **must never be used in production**:

| Setting                | Value in PyGoat            | Why It's Dangerous               |
|------------------------|----------------------------|----------------------------------|
| `DEBUG`                | `True`                     | Exposes full stack traces        |
| `SECRET_KEY`           | Hardcoded in `settings.py` | Allows session forgery           |
| `ALLOWED_HOSTS`        | Includes `0.0.0.0.`        | Overly permissive                |
| `SECRET_COOKIE_KEY`    | `"PYGOAT"` (plaintext)     | Trivially guessable              |
| Docker ports           | Exposed on `0.0.0.0`       | Accessible across the network    |

### Recommended Safe Deployment Checklist

- [ ] Run exclusively on `localhost` or a fully isolated VM / Docker network
- [ ] Never expose PyGoat to the public internet or a shared network
- [ ] Do not store real credentials or sensitive data anywhere near this app
- [ ] Use the provided `docker-compose.yml` for sandboxed lab environments
- [ ] Tear down the environment after each learning session

---

## 🔭 Responsible Disclosure Policy

We follow the principle of **coordinated responsible disclosure**:

1. Reporter submits the vulnerability privately via email
2. PyGoat maintainers acknowledge within 48 hours
3. A fix is developed and tested
4. The fix is released in a new version
5. A public advisory is published, crediting the reporter (unless they prefer to remain anonymous)

We ask that you:
- Give us reasonable time to fix the issue before going public
- Not exploit the vulnerability beyond what's needed to demonstrate it
- Not access, modify, or delete data that isn't yours

---

## 🤝 Credits & Recognition

Security researchers who responsibly disclose valid infrastructure vulnerabilities will be:

- Credited in the project's `CHANGELOG.md`
- Added to the contributors list (via `.all-contributorsrc`) under the 🛡️ `security` role
- Publicly thanked in the release notes for the fix

---

## 📚 Additional Resources

| Resource | Link |
|----------|------|
| OWASP PyGoat GitHub | https://github.com/adeyosemanputra/pygoat |
| OWASP Top 10 (2021) | https://owasp.org/Top10/ |
| MITRE CWE Top 25    | https://cwe.mitre.org/top25/ |
| Lab Solutions Guide | [`/Solutions/solution.md`](./Solutions/solution.md) |
| Developer Guide     | [`/docs/dev_guide.md`](./docs/dev_guide.md) |
| Django Security     | https://docs.djangoproject.com/en/4.2/topics/security/ |

---

*This security policy applies to the PyGoat infrastructure. The intentional vulnerabilities within the learning labs are features, not bugs. Thank you for helping keep PyGoat safe for learners everywhere. 🙏*
