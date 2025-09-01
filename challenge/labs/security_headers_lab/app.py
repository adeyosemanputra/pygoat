from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'security_headers_secret_key_2024'

USERS = {
    'john_doe': {
        'username': 'john_doe',
        'password': 'password123',
        'full_name': 'John Doe',
        'account_number': '****1234',
        'balance': 25000.00
    },
    'jane_smith': {
        'username': 'jane_smith', 
        'password': 'securepass',
        'full_name': 'Jane Smith',
        'account_number': '****5678',
        'balance': 15000.00
    }
}
TRANSACTIONS = []

def init_session():
    if 'user' not in session:
        session['user'] = None
    if 'secure_mode' not in session:
        session['secure_mode'] = False

def add_security_headers(response, secure_mode=False):
    if secure_mode:
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    else:
        response.headers.pop('X-Frame-Options', None)
        response.headers.pop('Content-Security-Policy', None)
        response.headers['X-Frame-Options'] = 'ALLOWALL'
    
    return response

@app.after_request
def after_request(response):
    secure_mode = session.get('secure_mode', False)
    return add_security_headers(response, secure_mode)

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    init_session()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session.modified = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    init_session()
    
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_data = USERS[session['user']]
    user_transactions = [t for t in TRANSACTIONS if t.get('from_user') == session['user']][-5:]
    
    return render_template('dashboard.html', user=user_data, transactions=user_transactions)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    init_session()
    
    if not session.get('user'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = request.form.get('amount', '0')
        recipient = request.form.get('recipient', '').strip()
        description = request.form.get('description', '').strip()
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            user_data = USERS[session['user']]
            if amount > user_data['balance']:
                return render_template('transfer.html', 
                                     error='Insufficient balance',
                                     user=user_data)
            
            user_data['balance'] -= amount
            
            transaction = {
                'id': str(uuid.uuid4())[:8],
                'from_user': session['user'],
                'from_name': user_data['full_name'],
                'recipient': recipient,
                'amount': amount,
                'description': description,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Completed'
            }
            TRANSACTIONS.append(transaction)
            
            return render_template('transfer.html', 
                                 success=f'Successfully transferred ₹{amount:.2f} to {recipient}',
                                 user=user_data,
                                 transaction=transaction)
            
        except ValueError as e:
            return render_template('transfer.html', 
                                 error=f'Invalid amount: {str(e)}',
                                 user=USERS[session['user']])
    
    return render_template('transfer.html', user=USERS[session['user']])

@app.route('/malicious')
def malicious():
    init_session()
    return render_template('malicious.html')

@app.route('/lab')
def lab():
    init_session()
    return render_template('lab.html')

@app.route('/solution')
def solution():
    init_session()
    return render_template('solution.html')

@app.route('/toggle_secure_mode')
def toggle_secure_mode():
    init_session()
    session['secure_mode'] = not session.get('secure_mode', False)
    session.modified = True
    
    return redirect(request.referrer or url_for('index'))

@app.route('/check_headers')
def check_headers():
    init_session()
    
    response = make_response(jsonify({
        'secure_mode': session.get('secure_mode', False),
        'message': 'Headers checked'
    }))
    
    response = add_security_headers(response, session.get('secure_mode', False))
    
    headers_info = {
        'secure_mode': session.get('secure_mode', False),
        'x_frame_options': response.headers.get('X-Frame-Options', 'Not Set'),
        'content_security_policy': response.headers.get('Content-Security-Policy', 'Not Set'),
        'x_content_type_options': response.headers.get('X-Content-Type-Options', 'Not Set'),
        'x_xss_protection': response.headers.get('X-XSS-Protection', 'Not Set'),
        'referrer_policy': response.headers.get('Referrer-Policy', 'Not Set')
    }
    
    return jsonify(headers_info)

@app.route('/demo_iframe')
def demo_iframe():
    init_session()
    return render_template('demo_iframe.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)