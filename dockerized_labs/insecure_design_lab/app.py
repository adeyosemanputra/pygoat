from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def gen_ticket():
    """Generate a random ticket code"""
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    """Description page explaining the insecure design lab"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Intentionally insecure
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!')
            return redirect(url_for('lab'))
        flash('Invalid credentials')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, password=password)  # Intentionally insecure
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Registration successful!')
        return redirect(url_for('lab'))
        
    return render_template('register.html')

@app.route('/lab', methods=['GET', 'POST'])
def lab():
    """Main lab page with ticket functionality"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        # Claim tickets
        if 'count' in request.form:
            try:
                count = request.form.get('count', type=int)
                if count:
                    user_ticket_count = len(user.tickets)
                    if (user_ticket_count + count) <= 5:
                        for _ in range(count):
                            ticket = Ticket(ticket_code=gen_ticket(), user_id=user.id)
                            db.session.add(ticket)
                        db.session.commit()
                    else:
                        error = "You can have at most 5 tickits"
            except:
                error = "Invalid input"
                    
        # Use ticket
        elif 'ticket' in request.form:
            try:
                ticket_code = request.form.get('ticket')
                all_tickets = Ticket.query.count()
                sold_tickets = all_tickets
                if sold_tickets < 60:  # Vulnerability: Fixed number makes it predictable
                    error = f"Wait until all tickets are sold ({60-sold_tickets} tickets left)"
                else:
                    ticket = Ticket.query.filter_by(ticket_code=ticket_code, user_id=user.id).first()
                    if ticket:
                        error = "Congratulation,You figured out the flaw in Design.<br> A better authentication should be used in case for checking the uniqueness of a user."
                    else:
                        error = "Invalid ticket"
            except:
                error = "Invalid input"

    return render_template('lab.html', tickets=[t.ticket_code for t in user.tickets], error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
