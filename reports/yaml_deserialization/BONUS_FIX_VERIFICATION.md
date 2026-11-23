# BONUS: Code Fix Verification - YAML Deserialization Vulnerability

## Executive Summary

The unsafe YAML deserialization vulnerability (B506) in the PyGoat application has been successfully remediated. Code changes replace `yaml.load()` with `yaml.safe_load()`, validate input structure, and improve error handling. Bandit scans confirm the vulnerability is eliminated.

---

## Vulnerability Details

**Issue:** CWE-502 — Deserialization of Untrusted Data  
**Bandit Rule:** B506 (yaml_load)  
**Severity:** Medium (Bandit assessment)  
**Confidence:** High  
**Location:** `dockerized_labs/a9_uckv_lab/app.py:62`

### Vulnerable Code
```python
data = yaml.load(file.stream, Loader=yaml.Loader)
```

The `yaml.Loader` permits instantiation of arbitrary Python objects through YAML tags like `!!python/object/apply`, enabling code execution during deserialization.

---

## Remediation Strategy

### 1. Replace Unsafe Loader with Safe Loader

**Before:**
```python
data = yaml.load(file.stream, Loader=yaml.Loader)
```

**After:**
```python
data = yaml.safe_load(file.stream)
```

The `safe_load()` function only deserializes simple types (dictionaries, lists, strings, numbers) and raises `yaml.YAMLError` on dangerous tags.

### 2. Add Input Validation

```python
if not isinstance(data, (dict, list)):
    flash("Invalid YAML format: expected a dictionary or list")
    logger.warning(f"Invalid YAML structure in {file.filename}")
    return redirect(url_for("lab1"))
```

Ensures the parsed YAML matches the expected structure before processing.

### 3. Improve Error Handling

```python
except yaml.YAMLError as e:
    flash(f"Invalid YAML file: {str(e)}")
    logger.error(f"YAML parsing error in {file.filename}: {str(e)}")
    return redirect(url_for("lab1"))
```

Separates YAML parsing errors from other exceptions, providing specific feedback.

---

## Full Fixed Code

### Updated `upload_yaml` Handler

```python
@app.route("/upload_yaml", methods=["POST"])
def upload_yaml():
    if "file" not in request.files:
        flash("No file selected")
        return redirect(url_for("lab1"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(url_for("lab1"))

    if file and allowed_file(file.filename):
        try:
            # FIXED: Use safe_load() to prevent arbitrary object instantiation
            data = yaml.safe_load(file.stream)
            
            # Validate that the parsed YAML is a dictionary
            if not isinstance(data, (dict, list)):
                flash("Invalid YAML format: expected a dictionary or list")
                logger.warning(f"Invalid YAML structure in {file.filename}")
                return redirect(url_for("lab1"))
            
            return render_template("result.html", content=data, filename=file.filename)
        except yaml.YAMLError as e:
            flash(f"Invalid YAML file: {str(e)}")
            logger.error(f"YAML parsing error in {file.filename}: {str(e)}")
            return redirect(url_for("lab1"))
        except Exception as e:
            flash(f"Error processing file: {str(e)}")
            logger.error(f"Unexpected error processing YAML file {file.filename}: {str(e)}")
            return redirect(url_for("lab1"))

    flash("Invalid file type")
    return redirect(url_for("lab1"))
```

---

## Bandit Scan Results

### Before Fix

```
Issue: [B506:yaml_load] Use of unsafe yaml load. Allows instantiation of arbitrary objects.
Severity: Medium   Confidence: High
Location: app.py:62:19
```

**Scan Output:**
```
Total issues (by severity):
  Undefined: 0
  Low: 0
  Medium: 1          ← VULNERABLE
  High: 0

Total issues (by confidence):
  Undefined: 0
  Low: 0
  Medium: 0
  High: 1
```

### After Fix

```
Test results:
  No issues identified.
```

**Scan Output:**
```
Total issues (by severity):
  Undefined: 0
  Low: 0
  Medium: 0          ← FIXED
  High: 0

Total issues (by confidence):
  Undefined: 0
  Low: 0
  Medium: 0
  High: 0
```

---

## Proof-of-Concept Demonstration

### Safe YAML File

**Input:** `test_safe.yaml`
```yaml
name: John Doe
age: 30
email: john@example.com
address:
  street: 123 Main St
  city: Springfield
  country: USA
phone_numbers:
  - 555-1234
  - 555-5678
```

**Result with both loaders:**
- ✓ `yaml.safe_load()`: Parses successfully
- ✓ `yaml.load(Loader=yaml.Loader)`: Parses successfully

### Malicious YAML - Subprocess Gadget

**Input:** `test_malicious_subprocess.yaml`
```yaml
!!python/object/apply:subprocess.Popen
- - echo
  - "This is a code execution payload"
```

**Result:**
- ✓ `yaml.safe_load()`: **BLOCKED** — `yaml.YAMLError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:subprocess.Popen'`
- ✗ `yaml.load(Loader=yaml.Loader)`: **CODE EXECUTED** — Creates and runs `subprocess.Popen` object

### Malicious YAML - OS System Gadget

**Input:** `test_malicious_os.yaml`
```yaml
!!python/object/apply:os.system
- id
```

**Result:**
- ✓ `yaml.safe_load()`: **BLOCKED** — `yaml.YAMLError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:os.system'`
- ✗ `yaml.load(Loader=yaml.Loader)`: **CODE EXECUTED** — Runs `os.system('id')`, outputs:
  ```
  uid=501(arturaipov) gid=20(staff) groups=20(staff),...
  ```

---

## Security Impact

### What the Fix Prevents

| Threat | Before Fix | After Fix |
|--------|-----------|-----------|
| Arbitrary object instantiation | ✗ Allowed | ✓ Blocked |
| Function calls via YAML tags | ✗ Allowed | ✓ Blocked |
| Remote code execution | ✗ Vulnerable | ✓ Protected |
| Subprocess execution | ✗ Vulnerable | ✓ Protected |
| File system access via gadgets | ✗ Vulnerable | ✓ Protected |
| Normal YAML parsing | ✓ Works | ✓ Works |

### Functionality Preserved

- Users can upload and parse valid YAML files
- Simple data structures (dictionaries, lists, strings, numbers) are fully supported
- Existing YAML processing logic remains unchanged
- Error messages are more informative

---

## Files Included

1. **report.md** — Full vulnerability analysis
2. **app_vulnerable.py** — Original vulnerable code
3. **app_fixed.py** — Fixed code with safe_load() and validation
4. **demo_vulnerability.py** — Proof-of-concept demonstration script
5. **test_safe.yaml** — Valid YAML test file
6. **test_malicious_subprocess.yaml** — Malicious YAML (subprocess gadget)
7. **test_malicious_os.yaml** — Malicious YAML (os.system gadget)
8. **bandit-b506.txt** — Bandit scan for original code
9. **bandit_before_after.txt** — Comparison of before and after scans

---

## Verification Steps

To verify the fix:

```bash
# 1. Scan the vulnerable code
python3 -m bandit -ll -ii -t B506 app_vulnerable.py -f txt
# Expected: 1 Medium severity issue (B506)

# 2. Scan the fixed code
python3 -m bandit -ll -ii -t B506 app_fixed.py -f txt
# Expected: No issues identified

# 3. Run the demonstration
python3 demo_vulnerability.py
# Shows yaml.safe_load() blocking malicious tags
```

---

## Recommendations

1. **Apply this fix to production:** Replace `yaml.load()` with `yaml.safe_load()` in the live application.
2. **Update documentation:** Document the YAML format requirements for uploaded files.
3. **Monitor input:** Log rejected YAML files (those that fail validation or parsing).
4. **Consider upgrade:** Evaluate upgrading PyYAML to the latest version for additional security patches.
5. **Audit other uses:** Search the codebase for other instances of `yaml.load()` with the full Loader.

---

## References

- [MITRE CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
- [Bandit B506: yaml_load](https://bandit.readthedocs.io/en/1.9.4/plugins/b506_yaml_load.html)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [OWASP Deserialization of Untrusted Data](https://owasp.org/www-community/Deserialization_of_untrusted_data)

---

**Verification Status:** ✓ COMPLETE  
**Security Assessment:** ✓ REMEDIATED  
**Bandit Confirmation:** ✓ NO ISSUES FOUND
