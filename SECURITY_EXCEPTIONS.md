# Security Exceptions — Acknowledged Unfixed Vulnerabilities

These vulnerabilities were detected by the automated DevSecOps pipeline but
**could not be automatically remediated**. Each must be reviewed and either
fixed manually or formally accepted as a known risk.

Generated: 2026-11-20T15:28:19.511778Z

## 1. Vulnerable Dependency: Flask
- **Severity**: LOW
- **File**: dockerized_labs/broken_auth_lab/requirements.txt
- **CVE**: CVE-2026-27205
- **Why it matters**: Flask version 2.3.3 contains 1 vulnerability/vulnerabilities (CVE-2026-27205). flask: Flask: Information disclosure via improper caching of session data
- **Recommended fix**: Update Flask in dockerized_labs/broken_auth_lab/requirements.txt to version 3.1.3 or higher.

## 2. Vulnerable Dependency: Jinja2
- **Severity**: MEDIUM
- **File**: dockerized_labs/broken_auth_lab/requirements.txt
- **CVE**: CVE-2024-22195, CVE-2024-34064, CVE-2024-56201, CVE-2024-56326, CVE-2025-27516
- **Why it matters**: Jinja2 version 3.1.2 contains 5 vulnerability/vulnerabilities (CVE-2024-22195, CVE-2024-34064, CVE-2024-56201, CVE-2024-56326, CVE-2025-27516). jinja2: HTML attribute injection when passing user input as keys to xmlattr filter jinja2: accepts keys containing non-attribute characters
- **Recommended fix**: Update Jinja2 in dockerized_labs/broken_auth_lab/requirements.txt to version 3.1.6 or higher.

## 3. Vulnerable Dependency: Werkzeug
- **Severity**: HIGH
- **File**: dockerized_labs/broken_auth_lab/requirements.txt
- **CVE**: CVE-2024-34069, CVE-2023-46136, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221, CVE-2026-102598, CVE-2026-21860, CVE-2026-27199
- **Why it matters**: Werkzeug version 2.3.7 contains 8 vulnerability/vulnerabilities (CVE-2024-34069, CVE-2023-46136, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221, CVE-2026-102598, CVE-2026-21860, CVE-2026-27199). python-werkzeug: user may execute code on a developer's machine python-werkzeug: high resource consumption leading to denial of service
- **Recommended fix**: Update Werkzeug in dockerized_labs/broken_auth_lab/requirements.txt to version 3.1.9 or higher.

## 4. Vulnerable Dependency: Flask
- **Severity**: LOW
- **File**: dockerized_labs/insec_des_lab/requirements.txt
- **CVE**: CVE-2026-27205
- **Why it matters**: Flask version 3.0.0 contains 1 vulnerability/vulnerabilities (CVE-2026-27205). flask: Flask: Information disclosure via improper caching of session data
- **Recommended fix**: Update Flask in dockerized_labs/insec_des_lab/requirements.txt to version 3.1.3 or higher.

## 5. Vulnerable Dependency: Werkzeug
- **Severity**: HIGH
- **File**: dockerized_labs/insec_des_lab/requirements.txt
- **CVE**: CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221, CVE-2026-102598, CVE-2026-21860, CVE-2026-27199
- **Why it matters**: Werkzeug version 3.0.1 contains 7 vulnerability/vulnerabilities (CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221, CVE-2026-102598, CVE-2026-21860, CVE-2026-27199). python-werkzeug: user may execute code on a developer's machine werkzeug: python-werkzeug: Werkzeug safe_join not safe on Windows
- **Recommended fix**: Update Werkzeug in dockerized_labs/insec_des_lab/requirements.txt to version 3.1.9 or higher.

## 6. Vulnerable Dependency: django
- **Severity**: CRITICAL
- **File**: dockerized_labs/sensitive_data_exposure/requirements.txt
- **CVE**: CVE-2023-31047, CVE-2025-64459, CVE-2023-36053, CVE-2023-43665, CVE-2023-46695, CVE-2024-24680, CVE-2025-57833, CVE-2025-64458, CVE-2026-15307, CVE-2023-41164, CVE-2024-27351, CVE-2024-45231, CVE-2025-48432, CVE-2026-15830, CVE-2026-53877, CVE-2026-53878, CVE-2026-48587, CVE-2026-48588, CVE-2026-6873, CVE-2026-8404
- **Why it matters**: django version 3.2.18 contains 20 vulnerability/vulnerabilities (CVE-2023-31047, CVE-2025-64459, CVE-2023-36053, CVE-2023-43665, CVE-2023-46695, CVE-2024-24680, CVE-2025-57833, CVE-2025-64458, CVE-2026-15307, CVE-2023-41164, CVE-2024-27351, CVE-2024-45231, CVE-2025-48432, CVE-2026-15830, CVE-2026-53877, CVE-2026-53878, CVE-2026-48587, CVE-2026-48588, CVE-2026-6873, CVE-2026-8404). python-django: Potential bypass of validation when uploading multiple files using one form field django: Django SQL injection
- **Recommended fix**: Update django in dockerized_labs/sensitive_data_exposure/requirements.txt to version 5.2.17, 6.0.8, 6.1.1 or higher.

## 7. Vulnerable Dependency: requests
- **Severity**: MEDIUM
- **File**: dockerized_labs/sensitive_data_exposure/requirements.txt
- **CVE**: CVE-2023-32681, CVE-2024-35195, CVE-2024-47081, CVE-2026-25645
- **Why it matters**: requests version 2.28.1 contains 4 vulnerability/vulnerabilities (CVE-2023-32681, CVE-2024-35195, CVE-2024-47081, CVE-2026-25645). python-requests: Unintended leak of Proxy-Authorization header requests: subsequent requests to the same host ignore cert verification
- **Recommended fix**: Update requests in dockerized_labs/sensitive_data_exposure/requirements.txt to version 2.33.0 or higher.

