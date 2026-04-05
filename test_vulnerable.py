import os
import hashlib

# SQL Injection vulnerability
def get_user(name):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cursor.execute(query)

# Hardcoded credential
DB_PASSWORD = "super_secret_password_123"

# Command injection
def run_deploy(url):
    os.system(f"git clone {url} /tmp/app")

# Weak hash algorithm
def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()

# Path traversal
def read_file(filename):
    with open(f"/data/{filename}") as f:
        return f.read()
