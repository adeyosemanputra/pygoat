from flask import Flask, render_template, request, make_response, redirect, url_for, session
import hashlib
import base64
import random
import time
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Scenario 1: Weak Encryption (MD5) - Lab data
SCENARIO1_USERS = {
    "user1": "e99a18c428cb38d5f260853678922e03",  # abc123
    "admin": "0192023a7bbd73250516f069df18b500",  # admin123
    "testuser": "5f4dcc3b5aa765d61d8327deb882cf99",  # password
}

# Scenario 2: Insecure Storage - Hardcoded key
HARDCODED_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='

# Scenario 3: Weak Randomness - Admin token generated at known time
ADMIN_TOKEN_TIMESTAMP = 1704063600  # January 1, 2024 00:00:00 UTC

# Scenario 4: CBC Bit-Flipping - Fixed key and IV
CBC_KEY = b'YELLOW_SUBMARINE'  # 16 bytes
CBC_IV = b'FEDCBA9876543210'   # 16 bytes


@app.route("/")
def index():
    return render_template("index.html")


# ==================== Scenario 1: Weak Encryption ====================
@app.route("/scenario1")
def scenario1_info():
    return render_template("scenario1_info.html")


@app.route("/scenario1/lab", methods=["GET", "POST"])
def scenario1_lab():
    context = {
        "admin_hash": SCENARIO1_USERS["admin"],
        "users_table": [
            {"username": "user1", "password_hash": SCENARIO1_USERS["user1"]},
            {"username": "admin", "password_hash": SCENARIO1_USERS["admin"]},
            {"username": "testuser", "password_hash": SCENARIO1_USERS["testuser"]},
        ]
    }
    
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if action == "register":
            if username and password:
                if username in SCENARIO1_USERS:
                    context["register_error"] = f"Username '{username}' already exists!"
                else:
                    password_hash = hashlib.md5(password.encode()).hexdigest()
                    SCENARIO1_USERS[username] = password_hash
                    context["register_success"] = True
                    context["user_hash"] = password_hash
                    context["users_table"].append({"username": username, "password_hash": password_hash})
            else:
                context["register_error"] = "Username and password required!"
        
        elif action == "login":
            if username and password:
                password_hash = hashlib.md5(password.encode()).hexdigest()
                if username in SCENARIO1_USERS and SCENARIO1_USERS[username] == password_hash:
                    context["login_success"] = True
                    context["logged_in_user"] = username
                    if username == "admin":
                        context["is_admin"] = True
                        context["flag"] = "FLAG{MD5_IS_BROKEN_USE_ARGON2}"
                else:
                    context["login_error"] = "Invalid credentials!"
            else:
                context["login_error"] = "Username and password required!"
    
    return render_template("scenario1_lab.html", **context)


# ==================== Scenario 2: Insecure Storage ====================
@app.route("/scenario2")
def scenario2_info():
    return render_template("scenario2_info.html")


@app.route("/scenario2/lab", methods=["GET", "POST"])
def scenario2_lab():
    from cryptography.fernet import Fernet
    
    cipher = Fernet(HARDCODED_KEY)
    
    encrypted_password = cipher.encrypt(b"SuperSecret123!").decode()
    encrypted_api_key = cipher.encrypt(b"sk-1234567890abcdef").decode()
    encrypted_flag = cipher.encrypt(b"FLAG{HARDCODED_KEYS_DESTROY_ENCRYPTION}").decode()
    
    context = {
        "encryption_key": HARDCODED_KEY.decode(),
        "encrypted_password": encrypted_password,
        "encrypted_api_key": encrypted_api_key,
        "encrypted_flag": encrypted_flag,
    }
    
    if request.method == "POST":
        user_key = request.form.get("encryption_key", "").strip()
        ciphertext = request.form.get("ciphertext", "").strip()
        
        if user_key and ciphertext:
            try:
                user_cipher = Fernet(user_key.encode())
                decrypted = user_cipher.decrypt(ciphertext.encode()).decode()
                context["decrypted_data"] = decrypted
                if "FLAG{" in decrypted:
                    context["is_flag"] = True
            except Exception:
                context["decrypt_error"] = "Invalid key or ciphertext!"
    
    return render_template("scenario2_lab.html", **context)


# ==================== Scenario 3: Weak Randomness ====================
@app.route("/scenario3")
def scenario3_info():
    return render_template("scenario3_info.html")


@app.route("/scenario3/lab", methods=["GET", "POST"])
def scenario3_lab():
    # Generate admin token with predictable seed
    random.seed(int(ADMIN_TOKEN_TIMESTAMP))
    admin_token = ''.join(random.choices('0123456789abcdef', k=32))
    
    # Current time token for demonstration
    current_time = int(time.time())
    random.seed(current_time)
    user_token = ''.join(random.choices('0123456789abcdef', k=32))
    
    context = {
        "admin_time": ADMIN_TOKEN_TIMESTAMP,
        "current_time": current_time,
        "user_token": user_token,
        "token_generated": False,
        "flag_found": False,
    }
    
    if request.method == "POST":
        if "action" in request.form and request.form["action"] == "generate":
            seed_value = request.form.get("seed", "").strip()
            if seed_value:
                try:
                    seed_int = int(seed_value)
                    random.seed(seed_int)
                    generated_token = ''.join(random.choices('0123456789abcdef', k=32))
                    context["token_generated"] = True
                    context["generated_token"] = generated_token
                    context["seed_used"] = seed_int
                except ValueError:
                    context["error"] = "Seed must be an integer"
        
        elif "action" in request.form and request.form["action"] == "submit":
            submitted_token = request.form.get("admin_token", "").strip()
            if submitted_token == admin_token:
                context["flag_found"] = True
                context["flag"] = "FLAG{PREDICTABLE_RANDOM_IS_NOT_RANDOM}"
            else:
                context["error"] = "Incorrect admin token!"
    
    return render_template("scenario3_lab.html", **context)


# ==================== Scenario 4: CBC Bit-Flipping ====================
@app.route("/scenario4")
def scenario4_info():
    return render_template("scenario4_info.html")


@app.route("/scenario4/lab", methods=["GET", "POST"])
def scenario4_lab():
    context = {
        "encryption_key": CBC_KEY.decode('latin-1'),
        "encryption_iv": CBC_IV.decode('latin-1'),
        "cookie_created": False,
        "access_granted": False,
        "access_denied": False,
    }
    
    def encrypt_cookie(plaintext):
        cipher = AES.new(CBC_KEY, AES.MODE_CBC, CBC_IV)
        padded = pad(plaintext.encode(), 16)
        ciphertext = cipher.encrypt(padded)
        return base64.b64encode(ciphertext).decode()
    
    def decrypt_cookie(cookie_b64):
        try:
            ciphertext = base64.b64decode(cookie_b64)
            cipher = AES.new(CBC_KEY, AES.MODE_CBC, CBC_IV)
            plaintext = unpad(cipher.decrypt(ciphertext), 16)
            return plaintext.decode('latin-1', errors='ignore')
        except:
            return None
    
    if request.method == "POST":
        action = request.form.get("action", "")
        
        if action == "create":
            username = request.form.get("username", "").strip()
            if username and len(username) <= 8:
                cookie_data = f"user={username};admin=0"
                encrypted = encrypt_cookie(cookie_data)
                context["cookie_created"] = True
                context["session_cookie"] = encrypted
                context["username"] = username
        
        elif action == "access":
            cookie = request.form.get("cookie", "").strip()
            if cookie:
                decrypted = decrypt_cookie(cookie)
                if decrypted:
                    context["decrypted_data"] = decrypted
                    if "admin=1" in decrypted:
                        context["access_granted"] = True
                        context["flag"] = "FLAG{CBC_WITHOUT_MAC_ALLOWS_TAMPERING}"
                    else:
                        context["access_denied"] = True
                        context["error_message"] = f"Admin access required. Decrypted: {decrypted}"
                else:
                    context["access_denied"] = True
                    context["error_message"] = "Invalid cookie or padding error"
    
    return render_template("scenario4_lab.html", **context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
