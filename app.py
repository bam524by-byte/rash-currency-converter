from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_mail import Mail, Message

from datetime import datetime

import requests
import stripe

# =====================================
# APP SETUP
# =====================================

app = Flask(__name__)

app.config['SECRET_KEY'] = 'rash_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rash.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =====================================
# EMAIL CONFIG
# =====================================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'

app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'your_email@gmail.com'

app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)

# =====================================
# STRIPE CONFIG
# =====================================

stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

# =====================================
# DATABASE
# =====================================

db = SQLAlchemy(app)

# =====================================
# LOGIN MANAGER
# =====================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'home'

# =====================================
# EXCHANGE API
# =====================================

API_URL = "https://open.er-api.com/v6/latest/"

currencies = [
    "USD",
    "UGX",
    "EUR",
    "GBP",
    "KES",
    "TZS",
    "NGN",
    "CAD",
    "AUD",
    "JPY"
]

# =====================================
# USER MODEL
# =====================================


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )
    is_premium = db.Column(
        db.Boolean,
        default=False
    )

    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# =====================================
# CONVERSION HISTORY MODEL
# =====================================

class ConversionHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100)
    )

    from_currency = db.Column(
        db.String(10)
    )

    to_currency = db.Column(
        db.String(10)
    )

    amount = db.Column(
        db.Float
    )

    result = db.Column(
        db.Float
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# =====================================
# USER LOADER
# =====================================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )
# =====================================
# HOME PAGE
# =====================================

@app.route('/')
def home():

    total_users = User.query.count()

    total_conversions = ConversionHistory.query.count()

    latest_history = ConversionHistory.query.order_by(
        ConversionHistory.created_at.desc()
    ).limit(5)

    return render_template(

        'index.html',

        currencies=currencies,

        total_users=total_users,

        total_conversions=total_conversions,

        latest_history=latest_history

    )

# =====================================
# REGISTER
# =====================================

@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']

    email = request.form['email']

    password = request.form['password']

    existing_user = User.query.filter(

        (User.username == username) |
        (User.email == email)

    ).first()

    if existing_user:

        flash("Username or Email already exists")

        return redirect(
            url_for('home')
        )

    hashed_password = generate_password_hash(
        password
    )

    user = User(

        username=username,

        email=email,

        password=hashed_password

    )

    db.session.add(user)

    db.session.commit()

    flash("Registration Successful")

    return redirect(
        url_for('home')
    )

# =====================================
# LOGIN
# =====================================

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

        return redirect(
            url_for('dashboard')
        )

    flash("Invalid Login")

    return redirect(
        url_for('home')
    )

# =====================================
# LOGOUT
# =====================================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect(
        url_for('home')
    )

# =====================================
# DASHBOARD
# =====================================

@app.route('/dashboard')
@login_required
def dashboard():

    total_users = User.query.count()

    total_conversions = ConversionHistory.query.count()

    my_history = ConversionHistory.query.filter_by(

        username=current_user.username

    ).order_by(

        ConversionHistory.created_at.desc()

    ).all()

    return render_template(

        'dashboard.html',

        username=current_user.username,

        premium=current_user.is_premium,

        total_users=total_users,

        total_conversions=total_conversions,

        my_history=my_history

    )
@app.route('/admin')
@login_required
def admin():

    users = User.query.all()

    total_users = User.query.count()

    total_conversions = ConversionHistory.query.count()

    premium_users = User.query.filter_by(
        is_premium=True
    ).count()

    return render_template(

        'admin.html',

        users=users,

        total_users=total_users,

        total_conversions=total_conversions,

        premium_users=premium_users

    )
# =====================================
# HISTORY PAGE
# =====================================

@app.route('/history')
def history():

    conversions = ConversionHistory.query.order_by(
        ConversionHistory.created_at.desc()
    ).all()

    return render_template(

        'history.html',

        conversions=conversions

    )
# =====================================
# CURRENCY CONVERTER
# =====================================

@app.route('/convert', methods=['POST'])
def convert():

    try:

        data = request.get_json()

        from_currency = data['from']

        to_currency = data['to']

        amount = float(
            data['amount']
        )

        response = requests.get(
            API_URL + from_currency
        )

        data_json = response.json()

        if 'rates' not in data_json:

            return jsonify({

                'success': False,

                'error': 'Exchange API Failed'

            })

        rates = data_json['rates']

        if to_currency not in rates:

            return jsonify({

                'success': False,

                'error': 'Currency Not Supported'

            })

        rate = rates[to_currency]

        converted = rate * amount

        username = "Guest"

        if current_user.is_authenticated:

            username = current_user.username

        history = ConversionHistory(

            username=username,

            from_currency=from_currency,

            to_currency=to_currency,

            amount=amount,

            result=converted

        )

        db.session.add(history)

        db.session.commit()

        return jsonify({

            'success': True,

            'result': round(converted, 2),

            'rate': round(rate, 4),

            'from': from_currency,

            'to': to_currency

        })

    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        })

# =====================================
# API STATUS
# =====================================

@app.route('/api-status')
def api_status():

    return jsonify({

        'status': 'online',

        'project': 'Rash Currency Converter',

        'developer': 'Rash Technologies'

    })

# =====================================
# RECENT CONVERSIONS API
# =====================================

@app.route('/recent-conversions')
def recent_conversions():

    history = ConversionHistory.query.order_by(

        ConversionHistory.created_at.desc()

    ).limit(10).all()

    data = []

    for item in history:

        data.append({

            'username': item.username,

            'from': item.from_currency,

            'to': item.to_currency,

            'amount': item.amount,

            'result': item.result,

            'date': item.created_at.strftime(
                "%Y-%m-%d %H:%M"
            )

        })

    return jsonify(data)

# =====================================
# TOTAL STATS API
# =====================================

@app.route('/stats')
def stats():

    total_users = User.query.count()

    total_conversions = ConversionHistory.query.count()

    premium_users = User.query.filter_by(
        is_premium=True
    ).count()

    return jsonify({

        'users': total_users,

        'conversions': total_conversions,

        'premium_users': premium_users

    })
# =====================================
# CONTACT FORM
# =====================================

@app.route('/contact', methods=['POST'])
def contact():

    try:

        name = request.form['name']

        email = request.form['email']

        message = request.form['message']

        msg = Message(

            'Rash Currency Converter Support',

            sender=app.config['MAIL_USERNAME'],

            recipients=[app.config['MAIL_USERNAME']]

        )

        msg.body = f"""
Name: {name}

Email: {email}

Message:
{message}
"""

        mail.send(msg)

        flash("Message Sent Successfully")

    except Exception as e:

        flash(f"Error Sending Message: {str(e)}")

    return redirect(
        url_for('home')
    )

# =====================================
# PREMIUM PAGE
# =====================================

@app.route('/premium')
@login_required
def premium():

    return render_template(
        'checkout.html'
    )
    checkout_session = stripe.checkout.Session.create(

        payment_method_types=['card'],

        line_items=[{

            'price_data': {

                'currency': 'usd',

                'product_data': {

                    'name': 'Rash Premium Plan'

                },

                'unit_amount': 500

            },

            'quantity': 1

        }],

        mode='payment',

        success_url='http://127.0.0.1:5000/payment-success',

        cancel_url='http://127.0.0.1:5000/payment-cancel'

    )

    return redirect(
        checkout_session.url
    )

# =====================================
# PAYMENT SUCCESS
# =====================================

@app.route('/payment-success')
@login_required
def payment_success():

    current_user.is_premium = True

    db.session.commit()

    flash("Premium Activated Successfully")

    return redirect(
        url_for('dashboard')
    )

# =====================================
# PAYMENT CANCEL
# =====================================

@app.route('/payment-cancel')
@login_required
def payment_cancel():

    flash("Payment Cancelled")

    return redirect(
        url_for('dashboard')
    )
@app.route('/profile')
@login_required
def profile():

    return render_template(
        'profile.html',
        user=current_user
    )
# =====================================
# AI ASSISTANT
# =====================================

@app.route('/ask-ai', methods=['POST'])
def ask_ai():

    data = request.get_json()

    question = data.get(
        'message',
        ''
    )

    answer = f"""
🤖 Rash AI Assistant

You Asked:
{question}

This is the demo AI response.

Future version will include:
• Forex Analysis
• Crypto Signals
• Trading Education
• Financial Tips
• Market News
"""

    return jsonify({

        'reply': answer

    })

# =====================================
# PREMIUM STATUS API
# =====================================

@app.route('/premium-status')
@login_required
def premium_status():

    return jsonify({

        'username': current_user.username,

        'premium': current_user.is_premium

    })
@app.route('/crypto-prices')
def crypto_prices():

    try:

        url = "https://api.coingecko.com/api/v3/simple/price"

        params = {
            "ids": "bitcoin,ethereum,tether",
            "vs_currencies": "usd"
        }

        response = requests.get(
            url,
            params=params
        )

        data = response.json()

        return jsonify({

            "btc": data["bitcoin"]["usd"],

            "eth": data["ethereum"]["usd"],

            "usdt": data["tether"]["usd"]

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })
    


@app.route('/market-data')
def market_data():

    try:

        usd = requests.get(
            API_URL + "USD"
        ).json()["rates"]

        eur = requests.get(
            API_URL + "EUR"
        ).json()["rates"]

        gbp = requests.get(
            API_URL + "GBP"
        ).json()["rates"]

        return jsonify({

            "usd_ugx": round(
                usd["UGX"], 2
            ),

            "eur_usd": round(
                eur["USD"], 4
            ),

            "gbp_usd": round(
                gbp["USD"], 4
            )

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })
    # crypto code here

    


# PASTE HERE 👇




    try:

        usd = requests.get(
            API_URL + "USD"
        ).json()["rates"]

        eur = requests.get(
            API_URL + "EUR"
        ).json()["rates"]

        gbp = requests.get(
            API_URL + "GBP"
        ).json()["rates"]

        return jsonify({

            "usd_ugx": round(
                usd["UGX"], 2
            ),

            "eur_usd": round(
                eur["USD"], 4
            ),

            "gbp_usd": round(
                gbp["USD"], 4
            )

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


# KEEP THIS AT THE VERY BOTTOM


        url = "https://api.coingecko.com/api/v3/simple/price"

        params = {
            "ids": "bitcoin,ethereum,tether",
            "vs_currencies": "usd"
        }

        response = requests.get(url, params=params)

        data = response.json()

        return jsonify({
            "btc": data["bitcoin"]["usd"],
            "eth": data["ethereum"]["usd"],
            "usdt": data["tether"]["usd"]
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })
# =====================================
# ERROR HANDLERS
# =====================================

@app.errorhandler(404)
def not_found(e):
    return """
    <h1>404</h1>
    <h2>Page Not Found</h2>
    <a href="/">Go Home</a>
    """, 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        '500.html'
    ), 500


# =====================================
# CONTEXT PROCESSOR
# =====================================

@app.context_processor
def inject_user():

    return dict(

        current_user=current_user

    )


# =====================================
# CREATE DATABASE TABLES
# =====================================

def create_database():

    with app.app_context():

        db.create_all()

        print(
            "Database Created Successfully"
        )


# =====================================
# APP START
# =====================================
@app.route('/settings')
@login_required
def settings():

    return render_template(
        'settings.html',
        user=current_user
    )
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'POST':

        old_password = request.form['old_password']
        new_password = request.form['new_password']

        if check_password_hash(
            current_user.password,
            old_password
        ):

            current_user.password = generate_password_hash(
                new_password
            )

            db.session.commit()

            flash(
                "Password Updated Successfully"
            )

            return redirect(
                url_for('profile')
            )

        flash("Old Password Incorrect")

    return render_template(
        'change_password.html'
    )
@app.route('/forex-dashboard')
def forex_dashboard():

    try:

        usd = requests.get(
            API_URL + "USD"
        ).json()["rates"]

        data = {

            "UGX": usd["UGX"],
            "KES": usd["KES"],
            "EUR": usd["EUR"],
            "GBP": usd["GBP"],
            "JPY": usd["JPY"]

        }

        return render_template(
            "forex_dashboard.html",
            data=data
        )

    except Exception as e:

        return str(e)
    
    
if __name__ == "__main__":

    create_database()

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )