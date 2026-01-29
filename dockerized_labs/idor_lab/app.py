from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simulated user database
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
                session['user_id'] = user_id
                session['username'] = username
                session['role'] = user['role']
                return redirect(url_for('lab'))
        
        return render_template('lab.html', error="Invalid credentials", show_login=True)
    
    return render_template('lab.html', show_login=True)


@app.route('/lab')
def lab():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('lab.html', 
                          current_user_id=session['user_id'],
                          current_username=session['username'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/user/<int:user_id>')
def get_user_profile(user_id):
    """
    VULNERABLE: Missing authorization check!
    Any authenticated user can access any user's data.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated. Please login first."}), 401
    
    # BUG: Should check if session['user_id'] == user_id
    
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    
    user_data = USERS[user_id].copy()
    del user_data['password']
    return jsonify(user_data)


@app.route('/api/users')
def list_users():
    if 'user_id' not in session:
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
