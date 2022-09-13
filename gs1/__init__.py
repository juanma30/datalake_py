import os
from flask import Flask, render_template, session
from datetime import timedelta


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='Postech2022!',
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE'),
    )
    app.permanent_session_lifetime = timedelta(minutes=30)

    from . import db

    from . import auth

    from . import indicadores

    from . import controls

    app.register_blueprint(auth.bp)
    app.register_blueprint(indicadores.bp)
    app.register_blueprint(controls.bp)

    @app.route('/')
    @auth.login_required
    def index():
        args = {
            'tiempo': session['last_login'],
            'usuario': session['name'],
            'rol': session['rol'],
            'show_title': False,
            'show_filter': False,
            'show_year': False
        }
        return render_template('index.html', **args)


    @app.route('/metas')
    @auth.check_rol
    def setMetas():
        args = {
            'tiempo': session['last_login'],
            'usuario': session['name'],
            'rol': session['rol'],
            'show_title': False,
            'show_filter': False,
            'show_year': True
        }
        return render_template('metas.html', **args)


    return app
