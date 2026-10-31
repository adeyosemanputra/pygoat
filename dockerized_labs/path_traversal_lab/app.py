from flask import Flask, render_template, request, abort
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health_check():
    return "OK", 200


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
    An absolute path such as /etc/passwd also leaves the uploads directory
    because os.path.join discards the base when the second part is absolute.
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

    is_traversal = ".." in filename or os.path.isabs(filename)
    return render_template(
        "result.html",
        success=True,
        filename=filename,
        content=content,
        is_traversal=is_traversal,
    )


def _is_inside_upload_dir(filepath):
    """Return True only if filepath is inside UPLOAD_DIR (not a sibling)."""
    base = os.path.realpath(UPLOAD_DIR)
    try:
        return os.path.commonpath([base, filepath]) == base
    except ValueError:
        return False


@app.route("/download/secure")
def download_secure():
    """
    SECURE ENDPOINT — resolve the real path and require it to share a
    common path with the uploads directory. A startswith() prefix check
    would accept sibling paths such as /app/uploads_backup.
    """
    filename = request.args.get("file")
    if not filename:
        abort(400, description="Missing 'file' parameter")

    filepath = os.path.realpath(os.path.join(UPLOAD_DIR, filename))

    if not _is_inside_upload_dir(filepath):
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
    app.run(host="0.0.0.0", port=5031)
