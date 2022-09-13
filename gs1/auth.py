import functools
from flask import (
    Blueprint, flash, g, render_template, url_for, request, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from gs1.db import get_db
from datetime import datetime


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        user = c.fetchone()

        if username is None:
            error = "Usuario y/o contraseña invalidos"
        if user is None or 'password' not in user.keys() or not check_password_hash(user['password'], password):
            error = "Usuario y/o contraseña invalidos"

        if error is None:
            c.execute(
                "update users set last_login = %s where id = %s",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id'])
            )
            db.commit()
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            session['name'] = user['nombre']
            session['rol'] = user['rol']
            session['last_login'] = user['last_login']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        username = request.form['username']
        nombre = request.form['name']
        apellido = request.form['lastname']
        password = request.form['password']
        error = None
        db, c = get_db()

        c.execute(
            "select * from users where username = %s", (username,)
        )
        if not username:
            error = "Se necesita un nombre de usuario valido"
        if not password:
            error = "Se necesita una contraseña"
        if not nombre:
            error = "Se necesita un nombre"
        if not apellido:
            error = "Se necesita un apellido"
        if c.fetchone() is not None:
            error = "El Usuario {} se encuentra registrado".format(username)

        if error is None:
            c.execute(
                "insert into users (username, nombre, apellido, password) values (%s, %s, %s, %s)",
                (username, nombre, apellido, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/registrar.html')


@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        g.user = c.fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def check_rol(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        else:
            if g.user['rol'] != 1:
                return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view
