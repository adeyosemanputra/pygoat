# YAML Deserialization Vulnerability Analysis

Lab 5 DevSecOps — Individual Task  
Analyzed vulnerability: Unsafe YAML Deserialization (Bandit B506)

## Overview

This directory contains a comprehensive analysis of the unsafe YAML deserialization vulnerability (CWE-502) found in the PyGoat application at `dockerized_labs/a9_uckv_lab/app.py:62`.

## Files

### Main Report
- **report.md** — Complete vulnerability analysis including:
  - How the issue was discovered (Bandit scan)
  - Technical explanation of why the code is unsafe
  - CWE classification (CWE-502: Deserialization of Untrusted Data)
  - CVSS v3.1 scoring (8.6-9.8 depending on deployment)
  - Impact assessment and required privileges
  - Suggested fix and recommendations

### Bonus: Code Fix and Verification
- **BONUS_FIX_VERIFICATION.md** — Complete remediation documentation:
  - Full fixed code with `yaml.safe_load()`
  - Before-and-after Bandit scan results
  - Proof-of-concept demonstration results
  - Security impact comparison

### Source Code
- **app_vulnerable.py** — Original vulnerable code extracted from the repo
- **app_fixed.py** — Fixed version using `yaml.safe_load()` with validation
- **demo_vulnerability.py** — Demonstration script showing the vulnerability in action

### Test Files
- **test_safe.yaml** — Valid YAML file (parses correctly with both loaders)
- **test_malicious_subprocess.yaml** — Malicious YAML using subprocess.Popen gadget
- **test_malicious_os.yaml** — Malicious YAML using os.system gadget

### Scan Reports
- **bandit-b506.txt** — Bandit scan output for B506 rule on the original repository
- **bandit_before_after.txt** — Detailed comparison of scans before and after the fix

## Quick Start

### View the Analysis
```bash
# Read the main vulnerability report
cat report.md

# Read the bonus fix verification
cat BONUS_FIX_VERIFICATION.md
```

### Run the Demonstration
```bash
# Show how yaml.safe_load() blocks malicious YAML
python3 demo_vulnerability.py
```

Expected output:
- ✓ Safe YAML: Parses correctly with both loaders
- ✓ Malicious YAML with `safe_load()`: **BLOCKED** with YAMLError
- ✗ Malicious YAML with `yaml.load(Loader=yaml.Loader)`: **CODE EXECUTED**

### Verify the Fix
```bash
# Scan vulnerable code
python3 -m bandit -ll -ii -t B506 app_vulnerable.py -f txt

# Scan fixed code
python3 -m bandit -ll -ii -t B506 app_fixed.py -f txt
```

Expected results:
- Vulnerable code: **1 Medium severity issue** (B506)
- Fixed code: **No issues identified**

## Key Findings

| Aspect | Details |
|--------|---------|
| Vulnerability | Unsafe YAML deserialization with `yaml.Loader` |
| CWE | CWE-502 (Deserialization of Untrusted Data) |
| Bandit Rule | B506 (yaml_load) |
| Severity | Medium (Bandit), High to Critical (CVSS 8.6-9.8) |
| Location | `dockerized_labs/a9_uckv_lab/app.py:62` |
| Impact | Remote Code Execution via YAML gadgets |
| Fix | Replace with `yaml.safe_load()` + input validation |

## What the Vulnerability Allows

An attacker can upload a malicious YAML file with special tags to:
1. Instantiate arbitrary Python objects
2. Call functions and methods
3. Execute system commands via `subprocess.Popen` or `os.system`
4. Read files, environment variables, and application secrets
5. Modify application state or disrupt service

## What the Fix Does

The fix replaces `yaml.load(file.stream, Loader=yaml.Loader)` with:

```python
data = yaml.safe_load(file.stream)
if not isinstance(data, (dict, list)):
    flash("Invalid YAML format: expected a dictionary or list")
    return redirect(url_for("lab1"))
```

This:
- ✓ Blocks object instantiation tags (`!!python/object`, `!!python/object/apply`)
- ✓ Only permits basic types (dict, list, string, number)
- ✓ Validates the parsed structure
- ✓ Provides clear error messages
- ✓ Preserves all existing functionality for valid YAML

## References

- [MITRE CWE-502](https://cwe.mitre.org/data/definitions/502.html)
- [Bandit B506 Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b506_yaml_load.html)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Original Repository](https://github.com/Retr0-46/lab5-NCS)

---

**Status:** Analysis Complete ✓  
**Fix Verified:** Yes ✓  
**Bandit Scan:** B506 Eliminated ✓
