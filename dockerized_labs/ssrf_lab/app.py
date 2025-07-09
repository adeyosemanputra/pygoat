from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for flash messages

@app.route('/')
def index():
    return render_template('index.html')

# Lab 1: File Reading SSRF
@app.route('/lab1', methods=['GET', 'POST'])
def lab1():
    if request.method == 'POST':
        file = request.form.get('blog')
        try:
            # Vulnerable implementation - allows directory traversal
            file_path = os.path.join(os.path.dirname(__file__), file)
            with open(file_path, "r") as f:
                blog_content = f.read()
            flash('Success! Keep exploring...', 'success')
            return render_template('lab1.html', blog=blog_content)
        except:
            return render_template('lab1.html', blog="No blog found")
    return render_template('lab1.html', blog="Read Blog About SSRF")

# Lab 2: URL SSRF with localhost check
@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            response = requests.get(url)
            flash('Successfully fetched URL!', 'success')
            return render_template('lab2.html', response=response.text)
        except:
            return render_template('lab2.html', error="Invalid URL")
    return render_template('lab2.html')

def get_client_ip(request):
    """Get client IP from request"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

# Internal endpoint for Lab 2
@app.route('/internal')
def internal():
    client_ip = get_client_ip(request)
    if client_ip == '127.0.0.1':
        return render_template('internal.html')
    return render_template('internal.html', access_denied=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
