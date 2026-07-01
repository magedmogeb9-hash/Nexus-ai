from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user
import random, phonenumbers
from phonenumbers import geocoder

auth_bp = Blueprint('auth', __name__)

def send_verification_email(email, code):
    print(f"[DEV] Verification code for {email}: {code}")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form.get('phone')
        company = request.form.get('company')
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))

        formatted_phone = None
        country = None
        if phone:
            try:
                parsed = phonenumbers.parse(phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    flash('Invalid phone number', 'danger')
                    return redirect(url_for('auth.register'))
                formatted_phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                country = geocoder.description_for_number(parsed, "en")
            except:
                flash('Phone format error, use international format', 'danger')
                return redirect(url_for('auth.register'))

        code = str(random.randint(100000, 999999))
        user = User(
            username=username,
            email=email,
            phone=formatted_phone,
            company=company,
            country=country,
            password_hash=generate_password_hash(password),
            verification_code=code
        )
        db.session.add(user)
        db.session.commit()
        send_verification_email(email, code)
        session['temp_user_id'] = user.id
        flash('Registered! Enter verification code', 'info')
        return redirect(url_for('auth.verify'))
    return render_template('register.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form['code']
        user_id = session.get('temp_user_id')
        if not user_id:
            return redirect(url_for('auth.register'))
        user = User.query.get(user_id)
        if user and user.verification_code == code:
            user.is_verified = True
            user.verification_code = None
            db.session.commit()
            login_user(user)
            session.pop('temp_user_id', None)
            flash('Verification successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Wrong code', 'danger')
    return render_template('verify.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash('Please verify your email first', 'warning')
                return redirect(url_for('auth.verify'))
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
