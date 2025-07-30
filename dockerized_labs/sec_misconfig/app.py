from flask import Flask, render_template, request, jsonify
import os
import traceback
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.debug = True  # Intentionally enabled for Lab 2

# Sensitive data for Lab 2
SENSITIVE_DATA = {
    'database_url': 'postgresql://admin:password123@localhost:5432/production',
    'api_key': 'sk_live_abcdef123456',
    'secret_key': 'secret356!werndt9038'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab1')
def lab1():
    return render_template('lab1.html')

@app.route('/lab1/get-secret')
def get_secret():
    if request.headers.get('X-Host') == 'admin.localhost:8000':
        secret = SENSITIVE_DATA['secret_key']
        return jsonify({'secret': secret})
    else:
        return jsonify({'secret': None})

@app.route('/lab1/check-auth')
def check_auth():
    auth_header = request.headers.get('X-Custom-Auth')
    if auth_header == 'SecretKey123':
        return jsonify({'success': True, 'message': 'Authentication successful!'})
    return jsonify({'success': False, 'message': 'Authentication failed.'})

@app.route('/lab2')
def lab2():
    return render_template('lab2.html')

@app.errorhandler(404)
def page_not_found(e):
# def trigger_error():
    # Sensitive configuration and credentials that would be exposed in debug mode
    app_config = {
        'SECRET_KEY': 'super_secret_production_key_123',
        'DATABASE_URI': 'postgresql://admin:secretpassword@production-db.internal:5432/users',
        'REDIS_PASSWORD': 'redis_prod_password_456',
        'AWS_ACCESS_KEY': 'AKIA1234567890ABCDEF',
        'AWS_SECRET_KEY': 'aws_secret_key_very_sensitive_789',
        'STRIPE_API_KEY': 'sk_live_1234567890abcdefghijklmnop',
        'ADMIN_CREDENTIALS': {
            'username': 'admin',
            'password': 'admin_secure_password_999'
        }
    }
    
    # Production API endpoints that shouldn't be exposed
    internal_apis = {
        'auth_service': 'http://internal-auth.prod:8080',
        'payment_service': 'http://internal-payments.prod:9000',
        'admin_panel': 'http://internal-admin.prod:8888'
    }
    
    # More sensitive environment variables
    os.environ['ENCRYPTION_KEY'] = 'encryption_key_should_not_be_exposed'
    os.environ['JWT_SECRET'] = 'jwt_signing_key_very_secret'
    os.environ['ADMIN_TOKEN'] = 'admin_access_token_highly_sensitive'

    # This will cause an error and expose all the above information in debug mode
    raise Exception("An intentional error was triggered to demonstrate a vulnerability.")
    return result

@app.route('/lab3')
def lab3():
    return render_template('lab3.html')

@app.route('/lab3/get-token', methods=['POST'])
def get_token():
    data = request.get_json()
    username = data.get('username', '')
    role = data.get('role', 'user')
    
    # Using a weak secret key (misconfiguration)
    secret = 'secret123'
    
    token = jwt.encode(
        {
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        secret,
        algorithm='HS256'
    )
    return jsonify({'token': token})

@app.route('/lab3/verify-token', methods=['POST'])
def verify_token():
    token = request.get_json().get('token', '')
    secret = 'secret123'
    
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        if payload['role'] == 'admin':
            return jsonify({
                'message': 'Success! You gained admin access.',
                'payload': payload
            })
        return jsonify({
            'message': 'Token verified but user is not admin',
            'payload': payload
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)
