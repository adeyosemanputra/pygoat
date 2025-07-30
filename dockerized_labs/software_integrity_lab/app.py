from flask import Flask, render_template, request, make_response, send_from_directory
import base64
import pickle
import os
from dataclasses import dataclass
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# For Lab 1 - Pickle Deserialization
@dataclass
class TestUser:
    admin: int = 0

# Create the initial pickled user data
pickled_user = pickle.dumps(TestUser())
encoded_user = base64.b64encode(pickled_user)

@app.route('/')
def index():
    """Description page explaining Software and Data Integrity Failures"""
    return render_template('index.html')

@app.route('/lab1')
def lab1():
    """Lab 1: Insecure Deserialization"""
    response = render_template('lab1.html', message="Only Admins can see this page")
    token = request.cookies.get('token')
    
    if token is None:
        token = encoded_user
        response = make_response(render_template('lab1.html', message="Only Admins can see this page"))
        response.set_cookie(key='token', value=token.decode('utf-8'))
    else:
        try:
            token = base64.b64decode(token)
            admin = pickle.loads(token)  # Intentionally vulnerable to pickle deserialization
            if admin.admin == 1:
                response = render_template('lab1.html', message="Welcome Admin, SECRETKEY:ADMIN123")
        except Exception as e:
            response = render_template('lab1.html', error=str(e))
            
    return response

@app.route('/lab2')
def lab2():
    """Lab 2: Software Supply Chain Attack"""
    username = request.args.get('username', '')
    if username:
        # Intentionally vulnerable to XSS that can modify download link
        return render_template('lab2.html', username=username, success=True)
    return render_template('lab2.html')

@app.route('/download/<path:filename>')
def serve_file(filename):
    """Serve static files with forced download"""
    return send_from_directory('static', filename, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    # Ensure static files exist
    static_dir = Path('./static')
    static_dir.mkdir(exist_ok=True)
    
    # Create sample files for lab2
    with open(static_dir / 'real.txt', 'w') as f:
        f.write("Congratulations! You downloaded the real file.")
    
    with open(static_dir / 'fake.txt', 'w') as f:
        f.write("This is a fake file that could contain malicious code.")
    
    app.run(host='0.0.0.0', port=5011, debug=True)
