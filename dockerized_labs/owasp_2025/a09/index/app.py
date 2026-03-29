from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader
import os

# Ensure Flask exits immediately on Docker SIGTERM to avoid shutdown delays
import signal
import sys

def shutdown_handler(signum, frame):
    print("Received shutdown signal")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
# End SIGTERM shutdown handler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, "templates")),          # lab templates
    FileSystemLoader(os.path.join(BASE_DIR, "shared_templates")),   # shared base.html
])

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
