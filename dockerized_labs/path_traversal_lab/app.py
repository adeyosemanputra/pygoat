from flask import Flask, render_template, request, send_file, abort
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

SAMPLE_FILES = {
    "report_q1.txt": "Q1 Financial Report\n\nRevenue: $1,200,000\nExpenses: $800,000\nNet Profit: $400,000\n",
    "team_roster.txt": "Engineering Team Roster\n\n1. Alice Johnson - Backend Lead\n2. Bob Smith - Frontend Dev\n3. Carol White - DevOps\n4. Dave Brown - QA Engineer\n",
    "meeting_notes.txt": "Meeting Notes - Sprint Planning\n\nDate: 2025-01-15\nAttendees: Engineering Team\n\nAction Items:\n- Migrate auth service to v2 API\n- Fix rate limiter edge case\n- Update deployment docs\n",
    "project_roadmap.txt": "Project Roadmap 2025\n\nQ1: Core platform stabilization\nQ2: New API gateway rollout\nQ3: Mobile app beta launch\nQ4: Enterprise feature pack\n",
}


def init_files():
    """Seed the uploads directory and the secret file on startup."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for name, content in SAMPLE_FILES.items():
        path = os.path.join(UPLOAD_DIR, name)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)

    secret_dir = os.path.join(BASE_DIR, "secret")
    os.makedirs(secret_dir, exist_ok=True)
    secret_file = os.path.join(secret_dir, "admin_credentials.txt")
    if not os.path.exists(secret_file):
        with open(secret_file, "w") as f:
            f.write(
                "=== ADMIN CREDENTIALS ===\n\n"
                "Username: superadmin\n"
                "Password: S3cur3P@ssw0rd!2025\n"
                "API Master Key: ak_live_7f8g9h0j1k2l3m4n5o6p\n\n"
                "FLAG: PATH_TRAVERSAL_SUCCESS_a01_2025\n"
            )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/lab")
def lab():
    files = os.listdir(UPLOAD_DIR)
    files = [f for f in files if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return render_template("lab.html", files=files)


@app.route("/download")
def download():
    """
    VULNERABLE ENDPOINT — no path sanitization.
    The filename from the query string is joined directly to the uploads
    directory, so ../../secret/admin_credentials.txt escapes the sandbox.
    """
    filename = request.args.get("file")
    if not filename:
        abort(400, description="Missing 'file' parameter")

    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.isfile(filepath):
        return render_template(
            "result.html",
            success=False,
            message=f"File not found: {filename}",
        )

    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception as e:
        return render_template(
            "result.html",
            success=False,
            message=f"Error reading file: {e}",
        )

    is_traversal = ".." in filename
    return render_template(
        "result.html",
        success=True,
        filename=filename,
        content=content,
        is_traversal=is_traversal,
    )


@app.route("/download/secure")
def download_secure():
    """
    SECURE ENDPOINT — resolves the real path and confirms it stays
    inside the uploads directory before serving the file.
    """
    filename = request.args.get("file")
    if not filename:
        abort(400, description="Missing 'file' parameter")

    filepath = os.path.realpath(os.path.join(UPLOAD_DIR, filename))

    if not filepath.startswith(os.path.realpath(UPLOAD_DIR)):
        return render_template(
            "result.html",
            success=False,
            message="Access denied — path traversal detected.",
            secure_mode=True,
        )

    if not os.path.isfile(filepath):
        return render_template(
            "result.html",
            success=False,
            message=f"File not found: {filename}",
            secure_mode=True,
        )

    with open(filepath, "r") as f:
        content = f.read()

    return render_template(
        "result.html",
        success=True,
        filename=filename,
        content=content,
        secure_mode=True,
    )


if __name__ == "__main__":
    init_files()
    app.run(host="0.0.0.0", port=5031, debug=True)
