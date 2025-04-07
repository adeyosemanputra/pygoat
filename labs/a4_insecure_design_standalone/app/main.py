from flask import Flask, render_template, request, redirect, session, url_for
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecurekey'  # for session handling

# Store tickets globally (for simplicity, simulate DB)
user_tickets = {}
all_tickets = []

MAX_TICKETS_PER_USER = 5
TOTAL_TICKETS = 60


def generate_ticket():
    return ''.join(random.choices(string.ascii_letters, k=10))


@app.route('/')
def index():
    return redirect(url_for('lab_info'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        session['username'] = username
        if username not in user_tickets:
            user_tickets[username] = []
        return redirect(url_for('lab'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/insecure-design')
def lab_info():
    return render_template('a11.html')


@app.route('/insecure-design_lab', methods=['GET', 'POST'])
def lab():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    tickets = user_tickets.get(username, [])

    if request.method == 'POST':
        if 'count' in request.form:
            count = int(request.form.get('count'))
            if len(tickets) + count <= MAX_TICKETS_PER_USER:
                for _ in range(count):
                    tkt = generate_ticket()
                    tickets.append(tkt)
                    all_tickets.append(tkt)
                user_tickets[username] = tickets
                return render_template('a11_lab.html', tickets=tickets, error=None)
            else:
                return render_template('a11_lab.html', tickets=tickets, error="You can have at most 5 tickets.")
        elif 'ticket' in request.form:
            ticket = request.form.get('ticket')
            sold_out = len(all_tickets) >= TOTAL_TICKETS
            if not sold_out:
                return render_template('a11_lab.html', tickets=tickets, error=f"Wait until all tickets are sold ({TOTAL_TICKETS - len(all_tickets)} remaining).")
            elif ticket in tickets:
                return render_template('a11_lab.html', tickets=tickets, error="🎉 You found the design flaw! Try fixing it now.")
            else:
                return render_template('a11_lab.html', tickets=tickets, error="❌ Invalid ticket.")

    return render_template('a11_lab.html', tickets=tickets, error=None)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
