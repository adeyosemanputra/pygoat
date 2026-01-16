from flask import Flask, render_template, request, jsonify
import os
import sys
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Simulated sensitive data
SENSITIVE_DATA = {
    "api_key": "sk_live_9876543210abcdef",
    "db_password": "SuperSecretPassword123!",
    "user_token": "token_xyz789",
    "encryption_key": "enc_key_abc123def456"
}

class TyposquattingPackage:
    """Simulated typosquatting package that mimics a popular library"""
    
    def __init__(self):
        print("[WARNING] Typosquatting package 'requets' loaded! ([typo]should be 'requests')")
        self.executed = True
        self.malicious_actions = []
        self.data_collected = []
    
    def collect_sensitive_info(self, context):
        """Malicious function that collects sensitive information"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": context.get("action", "unknown"),
            "data_stolen": {
                "sensitive_data": SENSITIVE_DATA,
                "environment": os.environ.get("FLASK_ENV", "production"),
                "python_path": sys.executable,
                "working_dir": os.getcwd(),
                "sys_path": sys.path[:3]  
            }
        }
        self.malicious_actions.append(record)
        self.data_collected.append(record)
        return record
    
    def execute_backdoor(self, command_type):
        """Simulated backdoor execution"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "type": "backdoor_execution",
            "command": command_type,
            "status": "executed"
        }
        self.malicious_actions.append(action)
        return action

# Simulate importing a typosquatting package
# Developer meant to install 'requests' but installed 'requets' (typo)
malicious_package = TyposquattingPackage()

# Simulate what happens when package is imported - executes immediately
print("[MALICIOUS] Package 'requets' initialized - executing malicious code...")
malicious_package.collect_sensitive_info({"action": "package_import"})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lab", methods=["GET", "POST"])
def lab():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "check_packages":
            packages = {
                "flask": "2.0.1",
                "requets": "2.28.1",  # Typosquatting (Should be 'requests')
                "pythn-dotenv": "0.19.0",  # Another typo! Should be 'python-dotenv'
                "pillow": "9.0.0"
            }
            return render_template("lab.html", packages=packages, show_packages=True)
        
        elif action == "use_api_call":
            # Simulate using the malicious package
            result = malicious_package.collect_sensitive_info({
                "action": "api_request",
                "endpoint": "/api/data",
                "stolen_data": SENSITIVE_DATA
            })
            return render_template("lab.html",
                api_result="API call completed successfully!",
                malicious_action=result,
                show_result=True
            )
        
        elif action == "execute_function":
            function_type = request.form.get("function_type", "default")
            result = malicious_package.execute_backdoor(function_type)
            return render_template("lab.html",
                exec_result="Function executed!",
                malicious_action=result,
                show_exec_result=True
            )
    
    return render_template("lab.html")

@app.route("/api/malicious-activity")
def malicious_activity():
    return jsonify({
        "status": "data_collected",
        "malicious_actions": malicious_package.malicious_actions,
        "data_collected": malicious_package.data_collected,
        "total_actions": len(malicious_package.malicious_actions),
        "warning": "⚠️ Malicious package detected and active!"
    })

@app.route("/api/check-packages", methods=["GET"])
def api_check_packages():
    """API endpoint to check installed packages"""
    packages = {
        "flask": "2.0.1",
        "requets": "2.28.1",  # Typosquatting!
        "pythn-dotenv": "0.19.0",  # Typosquatting!
        "pillow": "9.0.0"
    }
    return jsonify({
        "packages": packages,
        "total": len(packages),
        "note": "Check package names carefully for typos!"
    })

@app.route("/api/use-package", methods=["POST"])
def api_use_package():
    """API endpoint that uses the malicious package"""
    data = request.get_json()
    action_type = data.get("action_type", "api_call")
    
    if action_type == "api_call":
        result = malicious_package.collect_sensitive_info({
            "action": "api_request",
            "endpoint": "/api/data",
            "stolen_data": SENSITIVE_DATA,
            "user_agent": request.headers.get("User-Agent", "unknown")
        })
        return jsonify({
            "success": True,
            "message": "Package function executed successfully!",
            "malicious_action": result,
            "warning": "⚠️ Malicious code executed! Sensitive data collected!"
        })
    
    elif action_type == "backdoor":
        result = malicious_package.execute_backdoor(data.get("command", "default"))
        return jsonify({
            "success": True,
            "message": "Function executed!",
            "malicious_action": result,
            "warning": "⚠️ Backdoor command executed!"
        })
    
    return jsonify({"success": False, "error": "Unknown action type"})

@app.route("/api/verify-package", methods=["GET"])
def verify_package():
    """API endpoint to verify if a package is legitimate (vulnerable - doesn't properly check)"""
    package_name = request.args.get('name', '').strip().lower()
    
    if not package_name:
        return jsonify({'error': 'No package name provided'})

    legitimate_packages = {
        'requests': '2.28.1',
        'python-dotenv': '0.19.0',
        'flask': '2.0.1',
        'numpy': '1.23.0',
        'pillow': '9.0.0',
        'django': '4.0.0',
        'pandas': '1.5.0',
        'urllib3': '1.26.0'
    }
    
    # Simulate checking against a list of known typosquatting packages
    known_typos = {
        'requets': {
            'status': 'typosquatting',
            'correct_name': 'requests',
            'version': '2.28.1',
            'message': 'WARNING: This is a typosquatting package! The correct package name is "requests".',
            'risk': 'HIGH - This package may contain malicious code'
        },
        'pythn-dotenv': {
            'status': 'typosquatting',
            'correct_name': 'python-dotenv',
            'version': '0.19.0',
            'message': 'WARNING: This is a typosquatting package! The correct package name is "python-dotenv".',
            'risk': 'HIGH - This package may contain malicious code'
        }
    }
    
    if package_name in known_typos:
        result = known_typos[package_name]
        return jsonify({
            'package': package_name,
            'status': result['status'],
            'version': result.get('version', 'N/A'),
            'message': result['message'],
            'correct_name': result.get('correct_name'),
            'risk': result.get('risk')
        })

    if package_name in legitimate_packages:
        return jsonify({
            'package': package_name,
            'status': 'legitimate',
            'version': legitimate_packages[package_name],
            'message': 'Valid package! This is a legitimate package name.',
        })

    return jsonify({
        'package': package_name,
        'status': 'unknown',
        'message': 'Package not found in verification database. Proceed with caution!',
        'version': 'N/A'
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5021, debug=True)