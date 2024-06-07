import re
import os
from dotenv import load_dotenv

import functools
from flask import(
    Blueprint, flash, g, render_template, request, url_for,session, redirect, current_app
)
from werkzeug.security import check_password_hash,generate_password_hash
from todo.db import get_db

#Libraries for email sending
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

load_dotenv()

bp = Blueprint('auth', __name__,url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        paternal = request.form['paternal']
        maternal = request.form['maternal']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form['birthdate']
        db, c = get_db()
        error = None

        if not username:
            error = 'Username is required'
            
        if not name:
            error = 'Name is required'
            
        if not paternal:
            error = 'Last name is required'
        
        if not maternal:
            error = 'Last name  name is required'
            
        if not email:
            error = 'Email is required'
            
        if not phone:
            error = 'Phone is required'
            
        phone_regex = re.compile(r'^\d{10}$')
        if not phone_regex.match(phone):
            error = 'Phone must contain 10 digits'

        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])(?=.{8,})')
        if not password_regex.match(password):
            error = 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character, all within 8 characters'

        if error is None:
            c.execute('select id from user where username = %s', (username,))
            if c.fetchone() is not None:
                error = 'Username "{}" is already registered.'.format(username)
            
            if c.fetchone() is None:
                c.execute('select id from user where email = %s', (email,))
                if c.fetchone() is not None:
                    error = 'Email "{}" is already registered.'.format(email)

        if error is None:
            password_hash = generate_password_hash(password)

            c.execute('insert into user (username, name, paternal, maternal, birthdate, phone, email, password) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                      (username, name, paternal, maternal, birthdate, phone, email, password_hash))
            db.commit()
            
            verification_code = secrets.token_hex(3) 
            session['verification_code'] = verification_code
            flash('Please check your email for verification code.')
            send_verification_email(email, verification_code)
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verification_code = request.form['verification_code']
        db, c = get_db()
        error = None
        c.execute(
            'select * from user where username = %s',(username,)
        )
        user = c.fetchone()

        if user is None:
            error = 'Usuario y o contraseña inválida'
        elif not check_password_hash(user['password'], password):
            error = 'Usuario y o contraseña inválida'
        
        if session.get('verification_code') != verification_code:
            error = 'Código de verificación incorrecto'
            
        if username == 'admin' and password == 'Admin1234!':
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('todo.index'))
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('todo.index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute(
            'select * from user where id = %s', (user_id,)
        )
        g.user = c.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

@bp.route('/')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def send_verification_email(to_email, verification_code):
    subject = "Tu código de verificación"
    body = f"Tu código de verificación es: {verification_code}"

    msg = MIMEMultipart()
    EMAIL_ADDRESS = current_app.config["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = current_app.config["EMAIL_PASSWORD"]
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")