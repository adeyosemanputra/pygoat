from flask import Flask, render_template, request, make_response, redirect, url_for
import hashlib
import datetime
import base64

app = Flask(__name__)
app.secret_key = "crypto_failure_lab_secret_key"

# Lab 1 user data with MD5 hashes
LAB1_USERS = {
    "user1": "e99a18c428cb38d5f260853678922e03",  # abc123
    "admin": "21232f297a57a5a743894a0e4a801fc3",  # admin
    "user2": "d8578edf8458ce06fbc5bb76a58c5ca4"   # qwerty
}

# Lab 2 user data with SHA1 hashes
LAB2_USERS = {
    "user1": "40bd001563085fc35165329ea1ff5c5ecbdbbeef",  # 123
    "admin": "d033e22ae348aeb5660fc2140aec35850c4da997",  # admin
    "user2": "b1b3773a05c0ed0176787a4f1574ff0075f7521e"   # qwerty
}

def custom_hash(password):
    return hashlib.sha1(password.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab1', methods=['GET', 'POST'])
def lab1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if username in LAB1_USERS and LAB1_USERS[username] == password_hash:
            return render_template('lab1.html', user=username, success=True)
        else:
            return render_template('lab1.html', success=False, failure=True)
    return render_template('lab1.html')

@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = custom_hash(password)
        if username in LAB2_USERS and LAB2_USERS[username] == password_hash:
            return render_template('lab2.html', user=username, success=True)
        else:
            return render_template('lab2.html', success=False, failure=True)
    return render_template('lab2.html')

@app.route('/lab3', methods=['GET', 'POST'])
def lab3():
    if request.method == 'GET':
        try:
            cookie = request.cookies.get('cookie')
            if cookie:
                decoded_cookie = base64.b64decode(cookie).decode()
                username, expire = decoded_cookie.split('|')
                expire = datetime.datetime.fromisoformat(expire)
                now = datetime.datetime.now()
                if now > expire:
                    return render_template('lab3.html', success=False, failure=False)
                elif username == 'admin':
                    return render_template('lab3.html', success=True, failure=False, admin=True)
                else:
                    return render_template('lab3.html', success=True, failure=False, admin=False)
        except Exception as e:
            print(e)
            pass
        return render_template('lab3.html')
    
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # In a real app, you'd validate credentials here
        if username == "User" and password == "P@$$w0rd":
            expire = datetime.datetime.now() + datetime.timedelta(minutes=60)
            cookie_data = f"{username}|{expire}"
            encoded_cookie = base64.b64encode(cookie_data.encode()).decode()
            response = make_response(render_template('lab3.html', success=True, failure=False, admin=False, logged_in=True))
            response.set_cookie('cookie', encoded_cookie)
            return response
        else:
            response = make_response(render_template('lab3.html', success=False, failure=True))
            response.delete_cookie('cookie')
            return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
