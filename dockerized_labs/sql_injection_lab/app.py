from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from pathlib import Path

app = Flask(__name__, static_url_path='/labs/sql-injection/static')
BASE_PATH = '/labs/sql-injection'

def redirect_bp(path):
    """Redirect with BASE_PATH prefix"""
    return redirect(f"{BASE_PATH}{path}")

@app.context_processor
def inject_base_path():
    """Make BASE_PATH available in all templates"""
    return {'base_path': BASE_PATH}

app.config['SECRET_KEY'] = 'your-secret-key-here'

def init_db():
    db_path = Path('./database.db')
    if not db_path.exists():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        # Insert admin user
        c.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)", 
                 ('admin', '65079b006e85a7e798abecb99e47c154'))  # Original lab's admin password
        conn.commit()
        conn.close()

@app.route('/')
def index():
    """Main page with SQL injection lab description"""
    return render_template('index.html')

@app.route('/lab', methods=['GET', 'POST'])
def lab():
    """Lab page with the vulnerable login form"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Vulnerable SQL query construction (intentional)
        sql_query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            result = c.execute(sql_query).fetchone()
            conn.close()
            
            if result:
                return render_template('lab.html', logged_in_user=result[0], base_path=BASE_PATH)
            else:
                return render_template('lab.html', error='Invalid username or password', sql_query=sql_query, base_path=BASE_PATH)
        except sqlite3.Error as e:
            return render_template('lab.html', error=str(e), sql_query=sql_query, base_path=BASE_PATH)
            
    return render_template('lab.html', base_path=BASE_PATH)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    app.run(host='0.0.0.0', port=5012, debug=True)
