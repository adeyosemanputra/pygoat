from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

projects_data = {
    1: {
        "id": 1,
        "name": "Website Redesign",
        "description": "Update company website with modern design",
        "budget": "₹50,000",
        "client_credentials": "ABC-001",
        "internal_notes": "Client is very particular about colors",
        "team_members": ["john@company.com", "sarah@company.com"]
    },
    2: {
        "id": 2,
        "name": "Mobile App Development",
        "description": "Create mobile app for customer service",
        "budget": "₹2,50,000",
        "client_credentials": "DEF-456",
        "internal_notes": "Requires biometric authentication",
        "team_members": ["mike@company.com", "lisa@company.com"]
    },
    12: {
        "id": 12,
        "name": "Secret Launch",
        "description": "Top secret work",
        "budget": "₹2,00,00,000",
        "client_credentials": "XYZ-12345",
        "internal_notes": "NDA signed - highest confidentiality required",
        "team_members": ["ceo@company.com", "cto@company.com"]
    },
    15: {
        "id": 15,
        "name": "Database Migration",
        "description": "Migrate legacy database to new system",
        "budget": "₹75,000",
        "client_credentials": "GHI-789",
        "internal_notes": "Contains sensitive customer data",
        "team_members": ["admin@company.com", "db_admin@company.com"]
    }
}

users = {
    "user1": {"password": "password123", "role": "developer"},
    "user2": {"password": "pass456", "role": "manager"},
    "admin": {"password": "admin123", "role": "admin"}
}

current_user = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            current_user = {"username": username, "role": users[username]['role']}
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not current_user:
        return redirect(url_for('login'))
    
    project_list = []
    for project_id, project in projects_data.items():
        project_list.append({
            "id": project["id"],
            "name": project["name"],
            "description": project["description"]
        })
    
    return render_template('dashboard.html', projects=project_list, user=current_user)

@app.route('/api/project/<int:project_id>/details')
def get_project_details(project_id):
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401
    
    if project_id not in projects_data:
        return jsonify({"error": "Project not found"}), 404
    
    project = projects_data[project_id]
    
    return jsonify(project)

@app.route('/api/project/<int:project_id>/safe')
def get_project_safe(project_id):
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401
    
    if project_id not in projects_data:
        return jsonify({"error": "Project not found"}), 404
    
    project = projects_data[project_id]
    user_role = current_user.get('role', 'developer')
    
    safe_data = {
        "id": project["id"],
        "name": project["name"],
        "description": project["description"]
    }
    
    if user_role in ['manager', 'admin']:
        safe_data["team_members"] = project["team_members"]
    
    
    return jsonify(safe_data)

@app.route('/logout')
def logout():
    global current_user
    current_user = None
    return redirect(url_for('index'))

@app.route('/solution')
def solution():
    return render_template('solution.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)