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

bp = Blueprint('admin', __name__,url_prefix='/auth')

@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    db, c = get_db()

    # Fetch all users
    c.execute('SELECT * FROM user')
    users = c.fetchall()

    # Fetch all todos with user information
    c.execute('''
        SELECT t.*, u.username
        FROM todo AS t
        INNER JOIN user AS u ON t.id = u.id
    ''')
    todos_with_user = c.fetchall()

    # Improved logic for handling completed todos
    completed_todos = []
    incomplete_todos = []
    for todo in todos_with_user:
        if todo['completed'] == 1:
            completed_todos.append(todo)
        else:
            incomplete_todos.append(todo)

    return render_template('admin/admin.html', users=users, completed_todos=completed_todos, incomplete_todos=incomplete_todos)
