# IDOR (Insecure Direct Object Reference) Lab

A vulnerable web application demonstrating IDOR vulnerabilities for educational purposes.

## Category

**OWASP 2025: A01 - Broken Access Control**

## Description

This lab demonstrates how IDOR vulnerabilities allow attackers to access unauthorized data by manipulating object references in API endpoints.

The application has a user profile API at `/api/user/{user_id}`. While it checks if a user is authenticated, it fails to check if the user is authorized to access the requested data.

## Installation

### Using Docker

```bash
cd dockerized_labs/idor_lab
docker-compose up --build
```

Access at: **http://localhost:5030**

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Access at: **http://localhost:5030**

## Lab Credentials

| Username | Password | User ID | Role |
|----------|----------|---------|------|
| john | john123 | 1 | User |
| jane | jane123 | 2 | User |
| admin | ??? | 3 | Admin |

## Exploitation

1. Login as `john` with password `john123`
2. Note your User ID is `1`
3. Access `/api/user/1` - your own data (legitimate)
4. Change to `/api/user/3` - admin's SSN and salary exposed!

## Secure Fix

```python
@app.route('/api/user/<int:user_id>')
def get_user_profile(user_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Authorization check
    if session['user_id'] != user_id:
        if session.get('role') != 'admin':
            return jsonify({"error": "Forbidden"}), 403
    
    return jsonify(USERS[user_id])
```

## References

- [OWASP A01:2021 - Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

## Security Warning

⚠️ This lab contains intentionally vulnerable code for educational purposes. Do not use in production.
