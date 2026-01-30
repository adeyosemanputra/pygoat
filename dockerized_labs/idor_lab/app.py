from flask import Flask, render_template, request, jsonify, redirect, url_for
import secrets

app = Flask(__name__)
app.secret_key = 'idor_lab_secret_key_12345'

USERS = {
    1: {
        "id": 1,
        "username": "john",
        "password": "john123",
        "email": "john@example.com",
        "ssn": "123-45-6789",
        "salary": "$75,000",
        "role": "user",
        "department": "Engineering"
    },
    2: {
        "id": 2,
        "username": "jane",
        "password": "jane123",
        "email": "jane@example.com",
        "ssn": "987-65-4321",
        "salary": "$85,000",
        "role": "user",
        "department": "Marketing"
    },
    3: {
        "id": 3,
        "username": "admin",
        "password": "admin123",
        "email": "admin@company.com",
        "ssn": "111-22-3333",
        "salary": "$150,000",
        "role": "admin",
        "department": "Executive"
    },
}

TOKENS = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        for user_id, user in USERS.items():
            if user['username'] == username and user['password'] == password:
                token = secrets.token_urlsafe(16)
                TOKENS[token] = user_id
                return redirect(url_for('lab', token=token))
        
        return render_template('lab.html', error="Invalid credentials", show_login=True)
    
    return render_template('lab.html', show_login=True)


@app.route('/lab')
def lab():
    token = request.args.get('token')
    
    if not token or token not in TOKENS:
        return redirect(url_for('login'))
    
    user_id = TOKENS[token]
    user = USERS[user_id]
    
    return render_template('lab.html', 
                          current_user_id=user_id,
                          current_username=user['username'],
                          auth_token=token)


@app.route('/logout')
def logout():
    token = request.args.get('token')
    if token and token in TOKENS:
        del TOKENS[token]
    return redirect(url_for('index'))


@app.route('/api/user/<int:user_id>')
def get_user_profile(user_id):
    """VULNERABLE: No authorization check - any authenticated user can access any data"""
    token = request.args.get('token') or request.headers.get('X-Auth-Token')
    
    if not token or token not in TOKENS:
        return jsonify({"error": "Not authenticated. Please login first."}), 401
    
    # BUG: Should verify TOKENS[token] == user_id
    
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    
    user_data = USERS[user_id].copy()
    del user_data['password']
    return jsonify(user_data)


@app.route('/api/users')
def list_users():
    token = request.args.get('token') or request.headers.get('X-Auth-Token')
    
    if not token or token not in TOKENS:
        return jsonify({"error": "Not authenticated"}), 401
    
    users_list = []
    for user_id, user in USERS.items():
        users_list.append({
            "id": user_id,
            "username": user['username'],
            "department": user['department']
        })
    
    return jsonify({"users": users_list, "total": len(users_list)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030, debug=True)
