from flask import Flask, render_template, request, jsonify
import os
import sys
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Simulated sensitive data inside application
SENSITIVE_DATA = {
    "api_key": "sk_live_123456",
    "db_password": "SuperSecret123!",
    "user_token": "token_abc123"
}

class MaliciousDependency:
    """Simulated malicious dependency that steals data"""

    def __init__(self):
        print("[WARNING] Malicious dependency 'data-utils' loaded!")
        self.executed = True
        self.data_collected = []

    def collect_data(self, data):
        record = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.data_collected.append(record)
        return record

# Simulate importing malicious package
malicious_lib = MaliciousDependency()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/lab", methods=["GET", "POST"])
def lab():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "check_dependencies":
            dependencies = {
                "flask": "2.0.1",
                "requests": "2.28.1",
                "data-utils": "1.2.3",  # malicious package
                "common-helpers": "0.5.0"
            }
            return render_template("lab.html", dependencies=dependencies, show_dependencies=True)

        elif action == "use_feature":
            feature = request.form.get("feature")

            if feature == "process_data":
                result = malicious_lib.collect_data({
                    "action": "process_data",
                    "stolen_data": SENSITIVE_DATA,
                    "environment": os.environ.get("FLASK_ENV", "production")
                })

                return render_template("lab.html",
                    feature_result="Data processed successfully!",
                    data_collected=result,
                    show_result=True
                )

            elif feature == "get_config":
                config_data = {
                    "python_version": sys.version,
                    "working_directory": os.getcwd()
                }

                result = malicious_lib.collect_data({
                    "action": "config_access",
                    "config": config_data
                })

                return render_template("lab.html",
                    feature_result="Configuration retrieved!",
                    data_collected=result,
                    show_result=True
                )

    return render_template("lab.html")


@app.route("/api/exfiltrated-data")
def exfiltrated_data():
    return jsonify({
        "status": "data_collected",
        "records": malicious_lib.data_collected,
        "count": len(malicious_lib.data_collected)
    })

@app.route("/api/check-dependencies", methods=["GET"])
def api_check_dependencies():
    """API endpoint to check dependencies"""
    dependencies = {
        "flask": "2.0.1",
        "requests": "2.28.1",
        "data-utils": "1.2.3",  # malicious package
        "common-helpers": "0.5.0"
    }
    return jsonify({
        "dependencies": dependencies,
        "total": len(dependencies)
    })

@app.route("/api/use-feature", methods=["POST"])
def api_use_feature():
    """API endpoint to use application features"""
    data = request.get_json()
    feature = data.get("feature")
    
    if feature == "process_data":
        result = malicious_lib.collect_data({
            "action": "process_data",
            "stolen_data": SENSITIVE_DATA,
            "environment": os.environ.get("FLASK_ENV", "production")
        })
        return jsonify({
            "success": True,
            "message": "Data processed successfully!",
            "data_collected": result,
            "warning": "⚠️ Data collection detected!"
        })
    
    elif feature == "get_config":
        config_data = {
            "python_version": sys.version.split()[0],
            "working_directory": os.getcwd(),
            "app_secret": app.config['SECRET_KEY'][:10] + "..."
        }
        result = malicious_lib.collect_data({
            "action": "config_access",
            "config": config_data
        })
        return jsonify({
            "success": True,
            "message": "Configuration retrieved!",
            "data_collected": result,
            "warning": "⚠️ Configuration data accessed!"
        })
    
    return jsonify({"success": False, "error": "Unknown feature"})

@app.route("/api/check-package", methods=["GET"])
def check_package():
    """API endpoint to check if a package is safe (vulnerable - doesn't actually verify)"""
    package_name = request.args.get('name', '').strip().lower()
    
    if not package_name:
        return jsonify({'error': 'No package name provided'})
    
    # Check if it's the malicious package
    if package_name == 'data-utils':
        return jsonify({
            'package': package_name,
            'status': 'untrusted',
            'version': '1.2.3',
            'message': 'WARNING: This package has been flagged as potentially malicious! It may contain unauthorized code execution or data exfiltration capabilities.',
            'warning': 'This package is UNTRUSTED and should not be used!',
        })
    
    return jsonify({
        'package': package_name,
        'status': 'trusted',
        'version': 'latest',
        'message': 'Package appears safe',
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)
