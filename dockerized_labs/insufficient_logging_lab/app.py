from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # For flash messages

# Set up basic logging (intentionally insufficient)
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# User database (in memory for demonstration)
users = {
    'admin': {
        'password': 'secretpass123',
        'role': 'admin',
        'failed_attempts': 0
    }
}

def log_to_file(message):
    """Basic logging function (intentionally insufficient)"""
    with open('app.log', 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab1')
def lab1():
    return render_template('lab1.html')

@app.route('/lab1/login', methods=['POST'])
def lab1_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Vulnerable implementation - insufficient logging
    if username in users and users[username]['password'] == password:
        # Success case - no logging at all
        return redirect(url_for('lab2'))
    else:
        # Failed case - minimal logging
        log_to_file(f"Login failed for username: {username}")
        return render_template('lab1.html', error="Invalid credentials")

@app.route('/lab2')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/change_password', methods=['POST'])
def change_password():
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    
    if username in users:
        # Vulnerable - no logging of password changes
        users[username]['password'] = new_password
        return render_template('lab2.html', message=f"Password changed for {username}")
    return render_template('lab2.html', message="User not found")

@app.route('/lab2/change_role', methods=['POST'])
def change_role():
    username = request.form.get('username')
    new_role = request.form.get('new_role')
    
    if username in users:
        # Vulnerable - no logging of role changes
        old_role = users[username]['role']
        users[username]['role'] = new_role
        return render_template('lab2.html', message=f"Role changed for {username} from {old_role} to {new_role}")
    return render_template('lab2.html', message="User not found")

@app.route('/toggle-theme')
def toggle_theme():
    """Toggle between light and dark theme."""
    return '', 204

if __name__ == '__main__':
    # Create log file if it doesn't exist
    if not os.path.exists('app.log'):
        open('app.log', 'a').close()
        
    app.run(host='0.0.0.0', port=5014, debug=True)
