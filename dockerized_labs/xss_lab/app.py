from flask import Flask, render_template, request, redirect, make_response
import re

app = Flask(__name__)

# Mock FAANG data
FAANG_DATA = {
    'facebook': {
        'company': 'Facebook',
        'ceo': 'Mark Zuckerberg',
        'about': 'Social media and technology company'
    },
    'amazon': {
        'company': 'Amazon',
        'ceo': 'Andy Jassy',
        'about': 'E-commerce and technology company'
    },
    'apple': {
        'company': 'Apple',
        'ceo': 'Tim Cook',
        'about': 'Consumer electronics and software company'
    },
    'netflix': {
        'company': 'Netflix',
        'ceo': 'Ted Sarandos',
        'about': 'Streaming media and video on demand company'
    },
    'google': {
        'company': 'Google',
        'ceo': 'Sundar Pichai',
        'about': 'Technology and search engine company'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab1')
def lab1():
    q = request.args.get('q')
    if not q:
        return render_template('lab1.html')
    
    q_lower = q.lower()
    if q_lower in FAANG_DATA:
        data = FAANG_DATA[q_lower]
        return render_template('lab1.html', company=data['company'], ceo=data['ceo'], about=data['about'])
    else:
        # Vulnerable: Reflects unescaped user input
        return render_template('lab1.html', query=q)

@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    if request.method == 'POST':
        username = request.form.get('username', '')
        if username:
            # Vulnerable: Simple filter bypass by script tags
            username = username.strip()
            username = username.replace("<script>", "").replace("</script>", "")
            return render_template('lab2.html', username=username)
    return render_template('lab2.html', username='Guest')

@app.route('/lab3', methods=['GET', 'POST'])
def lab3():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # Vulnerable: Only filters alphanumeric
            pattern = r'\w'
            result = re.sub(pattern, '', username)
            return render_template('lab3.html', code=result)
    return render_template('lab3.html')

@app.route('/toggle-theme')
def toggle_theme():
    resp = make_response(redirect(request.referrer or '/'))
    current = request.cookies.get('theme', 'light')
    resp.set_cookie('theme', 'dark' if current == 'light' else 'light')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
