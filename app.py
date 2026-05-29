from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import requests
import stripe


app = Flask(__name__)

stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

app.config['SECRET_KEY'] = 'rash_secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rash.db'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)

API_URL = "https://open.er-api.com/v6/latest/"

currencies = [
    "USD","UGX","EUR","GBP","KES",
    "TZS","NGN","CAD","AUD",
    "JPY","BTC","ETH"
]

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(300)
    )

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))

@app.route('/')
def home():

    users = User.query.all()

    return render_template(
        'index.html',
        currencies=currencies,
        users=users
    )

@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']

    password = generate_password_hash(
        request.form['password']
    )

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        flash("User already exists")

        return redirect(url_for('home'))

    user = User(
        username=username,
        password=password
    )

    db.session.add(user)

    db.session.commit()

    flash("Registration Successful")

    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']

    password = request.form['password']

    user = User.query.filter_by(
        username=username
    ).first()

    if user and check_password_hash(
        user.password,
        password
    ):

        login_user(user)

        flash("Login Successful")

    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():

    users = User.query.all()

    total_users = len(users)

    return render_template(
        'dashboard.html',
        users=users,
        total_users=total_users
    )

@app.route('/contact', methods=['POST'])
def contact():

    name = request.form['name']

    email = request.form['email']

    message = request.form['message']

    msg = Message(
        'Rash Support Message',
        sender=email,
        recipients=['your_email@gmail.com']
    )

    msg.body = f"""
    Name: {name}

    Email: {email}

    Message:
    {message}
    """

    mail.send(msg)

    flash("Message Sent Successfully")

    return redirect(url_for('home'))

@app.route('/convert', methods=['POST'])
def convert():

    data = request.get_json()

    from_currency = data['from']

    to_currency = data['to']

    amount = float(data['amount'])

    response = requests.get(
        API_URL + from_currency
    )

    rates = response.json()['rates']

    converted = rates[to_currency] * amount

    return jsonify({
        'result': round(converted, 2),
        'rate': round(rates[to_currency], 4)
    })

@app.route('/premium')
@login_required
def premium():

    checkout_session = stripe.checkout.Session.create(

        payment_method_types=['card'],

        line_items=[{

            'price_data': {

                'currency': 'usd',

                'product_data': {

                    'name': 'Rash Premium Plan',

                },

                'unit_amount': 500,

            },

            'quantity': 1,

        }],

        mode='payment',

        success_url='http://127.0.0.1:5000/dashboard',

        cancel_url='http://127.0.0.1:5000/',

    )

    return redirect(checkout_session.url)

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)