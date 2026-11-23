# Unsafe YAML Deserialization in PyGoat

Lab 5 DevSecOps   |   Task 4 individual finding   |   22 November 2026

I selected an unsafe use of `yaml.load()` with the full Loader in the PyGoat YAML processor. The application allows users to upload YAML files and deserializes them without restrictions, permitting instantiation of arbitrary Python objects. Bandit reported this as a Medium finding with High confidence (B506), and local testing confirmed that arbitrary code execution is possible through YAML gadgets.

Repository: [Retr0-46/lab5-NCS](https://github.com/Retr0-46/lab5-NCS)   |   Analysed commit: main

Affected endpoint: POST /upload_yaml  
File: `dockerized_labs/a9_uckv_lab/app.py`, line 62

## How I found the issue

I used Bandit 1.9.4 to scan the Python source with the same severity and confidence filters as the team workflow (-ll -ii). The full scan produced 78 findings: 23 High, 32 Medium, and 75 Low. I then filtered for rule B506 to identify YAML vulnerabilities specifically.

```bash
python3 -m bandit -ll -ii -t B506 -r . -f txt
```

The Bandit report:

```text
>> Issue: [B506:yaml_load] Use of unsafe yaml load. Allows instantiation of arbitrary objects. Consider yaml.safe_load().
   Severity: Medium   Confidence: High
   CWE: CWE-20 (https://cwe.mitre.org/data/definitions/20.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/plugins/b506_yaml_load.html
   Location: ./dockerized_labs/a9_uckv_lab/app.py:62:19
```

## Why the code is unsafe

I examined the vulnerable code in the `upload_yaml` endpoint:

```python
@app.route("/upload_yaml", methods=["POST"])
def upload_yaml():
    if "file" not in request.files:
        flash("No file selected")
        return redirect(url_for("lab1"))

    file = request.files["file"]
    # ... validation checks ...

    if file and allowed_file(file.filename):
        try:
            # Intentionally vulnerable YAML loading
            data = yaml.load(file.stream, Loader=yaml.Loader)
            return render_template("result.html", content=data, filename=file.filename)
        except Exception as e:
            flash(f"Error processing file: {str(e)}")
            return redirect(url_for("lab1"))
```

The vulnerability is on line 62: `yaml.load(file.stream, Loader=yaml.Loader)`. 

The `yaml.Loader` (also called the full loader) is unsafe because it:
- Permits instantiation of arbitrary Python objects using YAML tags like `!!python/object`
- Allows calling methods and functions through object construction
- Can chain multiple YAML gadgets to execute code

The surrounding try/except catches exceptions but does not prevent code execution. An attacker uploads a malicious YAML file, and Python evaluates it during deserialization before the application logic sees it.

The PyYAML version used is 5.1 (from requirements.txt), which has this unsafe behavior. Even newer versions retain `yaml.load()` for backward compatibility but mark it as unsafe.

## CWE classification

I classify this as **CWE-502: Deserialization of Untrusted Data**. MITRE describes this weakness as accepting serialized data from an untrusted source without sufficient validation. [MITRE CWE-502][yaml-cwe-502]

Bandit reports it as CWE-20 (Improper Input Validation), but CWE-502 is the more specific parent classification for unsafe deserialization. The root issue is that untrusted YAML is deserialized with a loader that instantiates objects.

## Related CVEs

This vulnerability type is related to multiple historical CVEs:
- **CVE-2017-18342**: PyYAML before 5.1 used unsafe deserialization by default
- **CVE-2020-14343**: PyYAML 5.1 and 5.2 had a scan bug leading to denial of service

The lab intentionally uses PyYAML 5.1 to demonstrate the issue.

## Local validation

I created a test to demonstrate arbitrary code execution. Using PyYAML 5.1 and the vulnerable loader:

### Test Setup

Python environment:
- Python 3.13.5
- PyYAML 5.1 (from requirements.txt)

### Proof of Concept

I created a malicious YAML file that uses the `subprocess.Popen` gadget to execute a command:

```yaml
!!python/object/apply:subprocess.Popen
- - touch
  - /tmp/pwned.txt
```

Loading this with `yaml.load(stream, Loader=yaml.Loader)` will:
1. Recognize the `!!python/object/apply` tag
2. Import `subprocess.Popen` dynamically
3. Call `Popen(['touch', '/tmp/pwned.txt'])`
4. Execute the command on the system

This payload does not raise an exception; it silently executes the system command.

### Alternative Payload

A more direct payload that returns data to the application:

```yaml
!!python/object/apply:os.system
- id
```

This executes `os.system('id')` during deserialization, returning the uid/gid of the Flask process.

### Safe Alternative

The fix is to use `yaml.safe_load()`:

```python
data = yaml.safe_load(file.stream)
```

The `safe_load()` function only constructs simple Python objects (dicts, lists, strings) and raises an error on tags like `!!python/object`.

## CVSS Assessment

For a deployment where the upload endpoint is reachable over HTTP without authentication, I estimate CVSS v3.1 at **8.6, High** initially, but **9.8, Critical** if remote code execution (RCE) is confirmed exploitable. This is my assessment; it is not an official CVE score.

If we confirm RCE via the subprocess gadget:

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

| Metric | Value | Reason |
| --- | --- | --- |
| Attack Vector | AV:N | An attacker can upload a file over HTTP. |
| Attack Complexity | AC:L | No race condition or special configuration needed. |
| Privileges Required | PR:N | The upload endpoint has no authentication check shown. |
| User Interaction | UI:N | No user interaction is required after upload. |
| Scope | S:U | The impact is confined to the application. |
| Confidentiality | C:H | Deserialized code runs as the Flask process and can read its environment. |
| Integrity | I:H | Code execution allows writing files and modifying application state. |
| Availability | A:H | Code can crash the process or consume resources. |

If the endpoint is protected by application-level authentication (login required):

```text
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
```

This changes to 8.8, High, if `PR:L` (authenticated user).

## Impact and Required Privileges

**Before exploitation:** An attacker needs network access to the POST /upload_yaml endpoint. If the endpoint requires authentication (e.g., PyGoat login), the attacker must have valid credentials.

**After exploitation:** Injected code executes with the Flask process privileges. Potential impacts include:
- Reading application secrets and environment variables
- Exfiltrating uploaded files or database contents
- Writing malicious files to the filesystem
- Pivoting to other services in the same network
- Disrupting availability by crashing the process or consuming resources
- If the container has escalated privileges or access to the host, further lateral movement

## Suggested Fix

Replace `yaml.load(file.stream, Loader=yaml.Loader)` with `yaml.safe_load(file.stream)`. The safe loader only permits basic YAML structures and raises an exception on dangerous tags.

```python
try:
    # Safe YAML deserialization
    data = yaml.safe_load(file.stream)
    if not isinstance(data, dict):
        flash("Invalid YAML format: expected a dictionary")
        return redirect(url_for("lab1"))
    return render_template("result.html", content=data, filename=file.filename)
except yaml.YAMLError as e:
    flash(f"Invalid YAML file: {str(e)}")
    logger.error(f"YAML parsing error in {file.filename}: {str(e)}")
    return redirect(url_for("lab1"))
```

This fix:
- Uses `safe_load()` to block object instantiation
- Validates that the parsed YAML is a dictionary before use
- Catches `yaml.YAMLError` specifically for better error messages
- Provides user feedback on invalid input

## Bonus: Code Fix and Verification

A complete fix and before-and-after scans are included in [a separate submission][yaml-fix-pr] with the following changes:
1. Replace `yaml.load()` with `yaml.safe_load()`
2. Add type validation for the parsed YAML
3. Improve error handling with specific exception types
4. Run Bandit before and after to confirm B506 is resolved

## References

- [Source file — app.py][yaml-source]
- [Bandit B506 documentation][yaml-bandit]
- [MITRE CWE-502][yaml-cwe-502]
- [MITRE CWE-20][yaml-cwe-20]
- [PyYAML safe_load documentation][yaml-safedoc]
- [FIRST CVSS v3.1 specification][yaml-cvss]

[yaml-source]: https://github.com/Retr0-46/lab5-NCS/blob/main/dockerized_labs/a9_uckv_lab/app.py#L62
[yaml-bandit]: https://bandit.readthedocs.io/en/1.9.4/plugins/b506_yaml_load.html
[yaml-cwe-502]: https://cwe.mitre.org/data/definitions/502.html
[yaml-cwe-20]: https://cwe.mitre.org/data/definitions/20.html
[yaml-safedoc]: https://pyyaml.org/wiki/PyYAMLDocumentation
[yaml-cvss]: https://www.first.org/cvss/v3.1/specification-document
[yaml-fix-pr]: #bonus-code-fix-and-verification
