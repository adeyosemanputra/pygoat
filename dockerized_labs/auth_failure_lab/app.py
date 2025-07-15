from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from argon2 import PasswordHasher
import hashlib
import uuid
import random
import base64
import json

app = Flask("app")
app.config['SECRET_KEY'] = 'insecure-secret-key'  # Intentionally weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_locked = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    fail_attempts = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    lockout_cooldown = db.Column(db.DateTime)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    user = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Lab 1: OTP bypass vulnerability
stored_otps = {}
stored_admin_otp = None

# Lab 2: Default admin credentials - same as in the original lab
ADMIN_USERNAME = "admin_pygoat@pygoat.com"
ADMIN_PASSWORD = "2022_in_pygoat@pygoat.com"  # This will be hashed with Argon2

# Lab 3: Predefined users with SHA256 hashed passwords
# Passwords are: "password1", "password2", "password3", "password4"
USERS = {
    "User1": {"userid": "1", "username": "User1", "role": "user",
              "password": "0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e"},
    "User2": {"userid": "2", "username": "User2", "role": "user",
              "password": "6cf615d5bcaac778352a8f1f3360d23f02f34ec182e259897fd6ce485d7870d4"},
    "User3": {"userid": "3", "username": "User3", "role": "user",
              "password": "5906ac361a137e2d286465cd6588ebb5ac3f5ae955001100bc41577c3d751764"},
    "Admin": {"userid": "0", "username": "Admin", "role": "admin",
             "password": "b60d121b438a380c343d5ec3c2037564b82ffef3819eb9434d832d36dc948054"}
}

def init_db():
    with app.app_context():
        db.create_all()
        # Add admin user for Lab 2 if not exists
        if not Admin.query.filter_by(username=ADMIN_USERNAME).first():
            ph = PasswordHasher()
            admin = Admin(
                username=ADMIN_USERNAME,
                password=ph.hash(ADMIN_PASSWORD)
            )
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Lab 1: OTP Bypass Routes
@app.route('/lab1', methods=['GET', 'POST'])
def lab1():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            # Vulnerable: Short OTP, no rate limiting
            otp = str(random.randint(100, 999))
            if email == "admin@pygoat.com":
                global stored_admin_otp
                stored_admin_otp = otp
                # Vulnerable: Admin OTP not shown but predictable and no rate limiting
                response = make_response(render_template('lab1.html', otp_form=True))
                response.set_cookie('email', email)
                return response
            else:
                stored_otps[email] = otp
                response = make_response(render_template('lab1.html', otp_form=True, otp=otp))
                response.set_cookie('email', email)
                return response
    return render_template('lab1.html')

@app.route('/lab1/verify', methods=['POST'])
def verify_otp():
    email = request.cookies.get('email')
    otp = request.form.get('otp')
    if email == "admin@pygoat.com":
        # Vulnerable: No rate limiting, can brute force the 3-digit OTP
        if otp == stored_admin_otp:
            return render_template('lab1.html', email=email)
    elif email in stored_otps and otp == stored_otps[email]:
        return render_template('lab1.html', email=email)
    return render_template('lab1.html', otp_form=True)

# Lab 2: Admin Panel with Account Lockout
@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            user = Admin.query.filter_by(username=username).first()
            if not user:
                # Vulnerable: Username enumeration through different error message
                return render_template("lab2.html", success=False, failure=True, error="Invalid username")
            
            if user.is_locked and user.lockout_cooldown > datetime.now():
                # Vulnerable: Confirms account exists through lockout message
                return render_template("lab2.html", is_locked=True)
            
            try:
                ph = PasswordHasher()
                ph.verify(user.password, password)
                if user.is_locked and user.lockout_cooldown < datetime.now():
                    user.is_locked = False
                    user.last_login = datetime.now()
                    user.fail_attempts = 0
                    db.session.commit()
                return render_template("lab2.html", user=user, success=True)
            except:
                fail_attempts = user.fail_attempts + 1
                if fail_attempts == 5:
                    user.is_active = False
                    user.fail_attempts = 0
                    user.is_locked = True
                    user.lockout_cooldown = datetime.now() + timedelta(minutes=1440)
                    db.session.commit()
                    return render_template("lab2.html", success=False, failure=True, is_locked=True)
                user.fail_attempts = fail_attempts
                db.session.commit()
                # Vulnerable: Password-specific error message
                return render_template("lab2.html", success=False, failure=True, error="Invalid password")
        except Exception as e:
            return render_template("lab2.html", success=False, failure=True)
    return render_template("lab2.html")

# Lab 3: Session Management
@app.route('/lab3', methods=['GET', 'POST'])
def lab3():
    if request.method == "GET":
        try:
            session_id = request.cookies.get("session_id")
            if session_id:
                try:
                    # Vulnerable: Predictable session format and no signature verification
                    session_data = base64.b64decode(session_id).decode()
                    session_info = json.loads(session_data)
                    if session_info.get('valid_until') and datetime.fromisoformat(session_info['valid_until']) > datetime.now():
                        return render_template("lab3.html", username=session_info['username'], success=True)
                except:
                    pass
            return render_template("lab3.html")
        except:
            pass
        return render_template("lab3.html")
    
    elif request.method == "POST":
        if "username" not in request.form:
            response = make_response(render_template("lab3.html"))
            response.set_cookie("session_id", "", expires=0)
            return response

        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if username in USERS and USERS[username]["password"] == password_hash:
            # Vulnerable: Session information stored in cookie without signature
            session_data = {
                "username": username,
                "role": USERS[username]["role"],
                "valid_until": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            session_id = base64.b64encode(json.dumps(session_data).encode()).decode()
            
            response = make_response(render_template("lab3.html", success=True, username=username))
            response.set_cookie("session_id", session_id)
            return response

        return render_template("lab3.html", failure=True)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5007, debug=True)
