from flask import Flask, render_template, request, redirect, url_for, make_response, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))  # Vulnerable: Hardcoded secret key

# Vulnerable: Storing user data in memory
users = {
    'admin': {
        'password': generate_password_hash('admin123'),  # Vulnerable: Weak password
        'email': 'admin@example.com',
        'role': 'admin'
    },
    'user': {
        'password': generate_password_hash('password123'),  # Vulnerable: Weak password
        'email': 'user@example.com',
        'role': 'user'
    }
}

# Vulnerable: Storing reset tokens in memory
password_reset_tokens = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    if username in users and check_password_hash(users[username]['password'], password):  # Vulnerable: Plain text password comparison
        response = make_response(redirect(url_for('dashboard')))
        
        session.clear()
        session['username'] = username
            
        return response
    
    flash('Invalid username or password')
    return redirect(url_for('lab'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    # Vulnerable: No password complexity requirements
    if username and password and email:
        if username not in users:
            users[username] = {
                'password': generate_password_hash(password),  # Vulnerable: Storing plain text passwords
                'email': email,
                'role': 'user'
            }
            flash('Registration successful')
            return redirect(url_for('lab'))
    
    flash('Registration failed')
    return redirect(url_for('lab'))

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    
    # Vulnerable: Password reset token generation
    for username, user_data in users.items():
        if user_data['email'] == email:
            # Vulnerable: Predictable token generation
            token = secrets.token_urlsafe(32)
            password_reset_tokens[token] = username
            
            # In a real application, this would send an email
            # Vulnerable: Token exposed in response
            flash('Password reset link generated')
            return redirect(url_for('lab'))
    
    flash('Email not found')
    return redirect(url_for('lab'))

@app.route('/reset/<token>')
def reset_form(token):
    if token in password_reset_tokens:
        return render_template('reset.html', token=token)
    return 'Invalid token'

@app.route('/dashboard')
def dashboard():
    username = session.get('username')

    if not username or username not in users:
     return redirect(url_for('lab'))

    return render_template(
        'dashboard.html',
        username=username,
        role=users[username]['role'],
        email=users[username]['email']
    )
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Vulnerable: Debug mode enabled in production 