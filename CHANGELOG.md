# Pygoat v3.0.0 Pre

* Created standalone labs of existing pygoat labs

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

# Pygoat v2.0.1 Latest

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
