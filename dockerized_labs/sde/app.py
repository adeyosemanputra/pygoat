from flask import Flask, render_template, redirect
import os

app = Flask(__name__, static_url_path='/labs/sde/static')
BASE_PATH = '/labs/sde'

def redirect_bp(path):
    """Redirect with BASE_PATH prefix"""
    return redirect(f"{BASE_PATH}{path}")

@app.context_processor
def inject_base_path():
    """Make BASE_PATH available in all templates"""
    return {'base_path': BASE_PATH}


# Sensitive config data
app.config['SECRET_KEY'] = 'your-secret-key-here-not-very-secure'
app.config['DEBUG'] = True
app.config['DATABASE_URI'] = 'postgresql://admin:password123@localhost:5432/sensitive_db'
app.config['API_KEY'] = 'sk-1234567890abcdef'
app.config['PRIVATE_KEY'] = 'private-key-content-here'
app.config['TOKEN'] = 'access-token-xyz789'
app.config['SIGNATURE'] = 'signature-secret-key'
app.config['PASS'] = 'admin-password-123'

SENSITIVE_DATA = 'FLAGTHATNEEDSTOBEFOUND'


@app.route('/')
def index():
    return render_template('index.html', base_path=BASE_PATH)


@app.route('/lab')
def lab():
    return render_template('lab.html', base_path=BASE_PATH)

@app.route('/500error')
def trigger_error():
    # Intentional crash
    undefined_variable = some_undefined_variable
    return "This won't be reached"


@app.errorhandler(404)
def handle_404(e):
    # Dump the entire Flask config (including sensitive values)
    sensitive_dump = "\n".join(
        f"{k} = {v}" for k, v in app.config.items()
    )
    sensitive_dump += f"\nFLAG = {SENSITIVE_DATA}"
    raise RuntimeError(f"Invalid Route \n\n{sensitive_dump}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
