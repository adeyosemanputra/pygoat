from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for flash messages

BLOG_FILES = {
    "blog1": "blog1.txt",
    "blog2": "blog2.txt",
    "blog3": "blog3.txt",
    "blog4": "blog4.txt",
}
BLOG_DIR = os.path.join(os.path.dirname(__file__), "blogs")


@app.route("/")
def index():
    return render_template("index.html")


# Lab 1: File Reading SSRF
@app.route("/lab1", methods=["GET", "POST"])
def lab1():
    if request.method == "POST":
        blog_file = BLOG_FILES.get(request.form.get("blog"))
        if blog_file is None:
            return render_template("lab1.html", blog="No blog found")
        try:
            with open(os.path.join(BLOG_DIR, blog_file), "r", encoding="utf-8") as f:
                blog_content = f.read()
            flash("Success! Keep exploring...", "success")
            return render_template("lab1.html", blog=blog_content)
        except OSError:
            return render_template("lab1.html", blog="No blog found")
    return render_template("lab1.html", blog="Read Blog About SSRF")


# Lab 2: URL SSRF with localhost check
@app.route("/lab2", methods=["GET", "POST"])
def lab2():
    if request.method == "POST":
        url = request.form.get("url")
        try:
            response = requests.get(url)
            flash("Successfully fetched URL!", "success")
            return render_template("lab2.html", response=response.text)
        except:
            return render_template("lab2.html", error="Invalid URL")
    return render_template("lab2.html")


def get_client_ip(request):
    """Get client IP from request"""
    if "X-Forwarded-For" in request.headers:
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr


# Internal endpoint for Lab 2
@app.route("/internal")
def internal():
    client_ip = get_client_ip(request)
    if client_ip == "127.0.0.1":
        return render_template("internal.html")
    return render_template("internal.html", access_denied=True)

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
