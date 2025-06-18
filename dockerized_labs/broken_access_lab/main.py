from flask import Flask, render_template, request, make_response, redirect, url_for
from dataclasses import dataclass
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@dataclass
class User:
    username: str
    password: str
    is_admin: bool = False

# Hardcoded users for demonstration
users = {
    'jack': User('jack', 'jacktheripper', False),
    'admin': User('admin', 'admin_pass', True)
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/lab/login', methods=['POST'])
def lab_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in users and users[username].password == password:
        user = users[username]
        response = make_response(render_template('result.html', 
            username=username,
            message="Welcome back!" if not user.is_admin else "Welcome Admin! Secret key: ADMIN_KEY_123"))
        
        # Set admin cookie - intentionally vulnerable
        response.set_cookie('admin', '0' if not user.is_admin else '1', max_age=200)
        return response
    
    return render_template('result.html', message="Invalid credentials")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 