import re
import functools
from flask import(
    Blueprint, flash, g, render_template, request, url_for,session, redirect
)
from werkzeug.security import check_password_hash,generate_password_hash
from todo.db import get_db

bp = Blueprint('auth', __name__,url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None

        # Validate username
        if not username:
            error = 'Username is required'

        # Validate password complexity (regex)
        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])(?=.{8,})')
        if not password_regex.match(password):
            error = 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character, all within 8 characters'

        # Check for existing username
        if error is None:
            c.execute('select id from user where username = %s', (username,))
            if c.fetchone() is not None:
                error = 'Username "{}" is already registered.'.format(username)

        if error is None:
            # Secure password hashing
            password_hash = generate_password_hash(password)

            # Insert user into database
            c.execute('insert into user (username, password) values (%s, %s)',
                      (username, password_hash))
            db.commit()

            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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