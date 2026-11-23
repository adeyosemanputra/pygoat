# Lab 5 DevSecOps - Vulnerability Analysis Report

## 🎯 Task Overview

This repository contains the solution for Lab 5 DevSecOps assignment, which includes:

- SAST scanning with Bandit
- Docker image scanning with Docker Scout
- DAST scanning with OWASP ZAP
- Individual vulnerability analysis
- Code remediation (bonus)

## 📊 Scanning Results Summary

### SAST Scan (Bandit)

Total findings from full repository scan:
- **High severity:** 23 issues
- **Medium severity:** 32 issues
- **Low severity:** 75 issues

### Selected Individual Vulnerability

**Unsafe YAML Deserialization (CWE-502)**

- **Rule:** Bandit B506 (yaml_load)
- **Severity:** Medium (Bandit), High-Critical (CVSS 8.6-9.8)
- **Confidence:** High
- **Location:** `dockerized_labs/a9_uckv_lab/app.py:62`
- **Impact:** Remote Code Execution (RCE)

## 📁 Report Structure

```
reports/
├── path_traversal/          # Team member report (existing)
├── task4/                   # Team member report (existing)
└── yaml_deserialization/    # THIS SUBMISSION
    ├── report.md                    # Main vulnerability analysis
    ├── BONUS_FIX_VERIFICATION.md   # Code fix and verification
    ├── README.md                    # Quick guide
    ├── SUBMISSION_SUMMARY.md        # Executive summary
    │
    ├── Source Code:
    ├── app_vulnerable.py            # Original vulnerable code
    ├── app_fixed.py                 # Fixed code with safe_load()
    │
    ├── Demonstration:
    ├── demo_vulnerability.py        # PoC demonstration script
    ├── test_safe.yaml               # Valid YAML test file
    ├── test_malicious_subprocess.yaml  # Malicious payload (subprocess)
    ├── test_malicious_os.yaml       # Malicious payload (os.system)
    │
    └── Scan Reports:
        ├── bandit-b506.txt          # B506 scan results
        ├── bandit_before_after.txt  # Before/after comparison
        └── bandit-full.json         # Full Bandit scan (JSON)
```

## 🔍 Vulnerability Details

### What is the vulnerability?

The application uses `yaml.load(file.stream, Loader=yaml.Loader)` to parse user-uploaded YAML files. This loader permits instantiation of arbitrary Python objects through YAML tags like:

```yaml
!!python/object/apply:subprocess.Popen
- - echo
  - "malicious command"
```

### Why is it dangerous?

An attacker can:
1. Execute arbitrary system commands
2. Read application secrets and environment variables
3. Modify files accessible to the Flask process
4. Disrupt service availability
5. Potentially pivot to other services

### CVSS Assessment

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Score: 9.8 (Critical) without authentication
Score: 8.8 (High) with authentication required
```

## 🛠️ Remediation (Bonus)

### The Fix

Replace unsafe deserialization:

```python
# BEFORE (VULNERABLE)
data = yaml.load(file.stream, Loader=yaml.Loader)
```

```python
# AFTER (FIXED)
data = yaml.safe_load(file.stream)
if not isinstance(data, (dict, list)):
    flash("Invalid YAML format: expected a dictionary or list")
    return redirect(url_for("lab1"))
```

### Verification

**Before fix:**
```
Bandit B506: 1 Medium severity issue found
Code execution: ✗ VULNERABLE
```

**After fix:**
```
Bandit B506: No issues identified
Code execution: ✓ BLOCKED
```

## 🧪 Running the Demonstration

### Prerequisites

```bash
# Install required packages
pip install pyyaml bandit
```

### Run the PoC

```bash
cd reports/yaml_deserialization
python3 demo_vulnerability.py
```

Expected output:
- ✅ Safe YAML: Parses successfully with both loaders
- ✅ Malicious YAML + `safe_load()`: **BLOCKED** with YAMLError
- ❌ Malicious YAML + `yaml.load()`: **CODE EXECUTED**

### Verify the Fix

```bash
# Scan vulnerable code
python3 -m bandit -ll -ii -t B506 app_vulnerable.py -f txt

# Scan fixed code  
python3 -m bandit -ll -ii -t B506 app_fixed.py -f txt
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Main Report](reports/yaml_deserialization/report.md) | Complete vulnerability analysis with CWE, CVSS, and impact |
| [Bonus Verification](reports/yaml_deserialization/BONUS_FIX_VERIFICATION.md) | Code fix with before/after scans |
| [Submission Summary](reports/yaml_deserialization/SUBMISSION_SUMMARY.md) | Executive summary for review |
| [Quick Guide](reports/yaml_deserialization/README.md) | Quick start and file overview |

## ✅ Assignment Checklist

### Required

- [x] Individual vulnerability selected (B506 - YAML deserialization)
- [x] CWE classification (CWE-502)
- [x] CVSS score and vector (9.8 / CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- [x] Impact analysis
- [x] Required privileges analysis
- [x] Detailed report (report.md)

### Bonus

- [x] Code fix implemented (app_fixed.py)
- [x] Bandit scan before/after (bandit_before_after.txt)
- [x] Proof of concept demonstration (demo_vulnerability.py)
- [x] Verification documentation (BONUS_FIX_VERIFICATION.md)

## 🔗 References

- [Original Repository](https://github.com/Retr0-46/lab5-NCS)
- [MITRE CWE-502](https://cwe.mitre.org/data/definitions/502.html)
- [Bandit B506 Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b506_yaml_load.html)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [FIRST CVSS v3.1](https://www.first.org/cvss/v3.1/specification-document)

## 👤 Author

**Individual Assignment Submission**  
Lab 5 DevSecOps  
Date: 22 November 2026

---

**Status:** ✅ Complete  
**Bonus:** ✅ Included  
**Verification:** ✅ Passed
