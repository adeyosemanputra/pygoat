from flask import Flask, request, render_template, redirect, session
from datetime import datetime
from jinja2 import ChoiceLoader, FileSystemLoader
import os
import signal
import sys

# -----------------------------------------
# Graceful shutdown for Docker
# -----------------------------------------
def shutdown_handler(signum, frame):
    print("Received shutdown signal")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
# -----------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    FileSystemLoader(os.path.join(BASE_DIR, "shared_templates")),
])

app.secret_key = "dev-secret"

# Immutable credentials ONLY
USERS = {
    "alice": {"password": "alicepass"},
    "bob": {"password": "bobpass"},
}

SECURITY_LOGS = []
LAST_ALERT = {"message": None}

LAB_MODE = {"mode": "vulnerable"}  # vulnerable | secure


# -----------------------------------------
# Logging helpers (actor-role aware)
# -----------------------------------------
def log_event(event_type, details=None, actor_role=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "username": session.get("user"),
        "current_role": actor_role if actor_role else session.get("role"),
        "ip": request.remote_addr,
        "details": details,
        "severity": "INFO",
    }
    SECURITY_LOGS.append(entry)
    print("[LOG]", entry)


def alert_event(event_type, details=None, actor_role=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "username": session.get("user"),
        "current_role": actor_role if actor_role else session.get("role"),
        "ip": request.remote_addr,
        "details": details,
        "severity": "ALERT",
    }
    SECURITY_LOGS.append(entry)
    LAST_ALERT["message"] = event_type
    print("[ALERT 🚨]", entry)


# -----------------------------------------
# Helpers
# -----------------------------------------
def current_user():
    if "user" not in session:
        return None
    return {
        "username": session["user"],
        "role": session.get("role", "user"),
    }


# -----------------------------------------
# Routes
# -----------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]

        if username in USERS and USERS[username]["password"] == pw:
            session["user"] = username
            session["role"] = "admin" if username == "bob" else "user"
            return redirect("/dashboard")

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect("/")

    alert = LAST_ALERT["message"]
    LAST_ALERT["message"] = None

    ui_warning = session.pop("ui_warning", None)

    return render_template(
        "dashboard.html",
        username=session.get("user"),
        role=user["role"],
        mode=LAB_MODE["mode"],
        alert=alert,
        ui_warning=ui_warning,
    )


@app.route("/audit")
def audit():
    if not current_user():
        return redirect("/")
    return render_template("audit.html", logs=SECURITY_LOGS)


@app.route("/toggle-mode")
def toggle_mode():
    LAB_MODE["mode"] = "secure" if LAB_MODE["mode"] == "vulnerable" else "vulnerable"
    return redirect("/dashboard")


# -----------------------------------------
# Core Logic
# -----------------------------------------
@app.route("/change-role", methods=["POST"])
def change_role():
    user = current_user()
    if not user:
        return redirect("/")

    requested_role = request.form.get("role")
    workflow = request.form.get("workflow", "ui")   # visible decoy
    is_internal = request.form.get("internal")      # real flaw

    current_role = user["role"]

    # -------------------------------
    # NO-OP
    # -------------------------------
    if requested_role == current_role:
        return redirect("/dashboard")

    # -------------------------------
    # VULNERABLE MODE
    # -------------------------------
    if LAB_MODE["mode"] == "vulnerable":

        # Admin allowed to change roles
        if current_role == "admin":
            old_role = current_role

            log_event(
                "ADMIN_ROLE_CHANGE",
                {
                    "from_role": old_role,
                    "to_role": requested_role,
                    "workflow": workflow,
                },
                actor_role=old_role,
            )

            session["role"] = requested_role
            return redirect("/dashboard")

        # ❌ Silent privilege escalation
        if is_internal:
            old_role = current_role

            log_event(
                "ROLE_CHANGE",
                {
                    "from_role": old_role,
                    "to_role": requested_role,
                    "workflow": workflow,
                    "method": "implicit_internal_context",
                    "alert_triggered": False,
                },
                actor_role=old_role,
            )

            session["role"] = requested_role
            return redirect("/dashboard")

        # UI request → INFO + UI notice
        log_event(
            "ROLE_CHANGE_REQUEST",
            {
                "requested_role": requested_role,
                "workflow": workflow,
                "note": "User-initiated request",
            },
            actor_role=current_role,
        )

        session["ui_warning"] = "Role change request recorded (workflow: ui)"
        return redirect("/dashboard")

    # -------------------------------
    # SECURE MODE
    # -------------------------------
    if LAB_MODE["mode"] == "secure":

        # UI request by non-admin → BLOCK silently
        if current_role != "admin" and not is_internal:
            log_event(
                "ROLE_CHANGE_REQUEST_BLOCKED",
                {
                    "requested_role": requested_role,
                    "workflow": workflow,
                    "mode": "secure",
                    "note": "Blocked by policy",
                },
                actor_role=current_role,
            )
            session["ui_warning"] = "Role change request blocked by security policy"
            return redirect("/dashboard")

        # Malicious/internal attempt → ALERT
        if current_role != "admin" and is_internal:
            alert_event(
                "BLOCKED_PRIVILEGE_ESCALATION",
                {
                    "requested_role": requested_role,
                    "workflow": workflow,
                    "internal_context_present": True,
                },
                actor_role=current_role,
            )
            return redirect("/dashboard")

        # Legit admin role change
        old_role = current_role

        log_event(
            "ADMIN_ROLE_CHANGE_SECURE",
            {
                "from_role": old_role,
                "to_role": requested_role,
                "workflow": workflow,
            },
            actor_role=old_role,
        )

        session["role"] = requested_role
        return redirect("/dashboard")


@app.route("/secure-fix")
def secure_fix():
    return render_template("secure-fix.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
