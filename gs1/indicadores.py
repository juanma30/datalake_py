from flask import (
    Blueprint, flash, g, render_template, url_for, request, session, redirect
)
from gs1.auth import login_required
from gs1.functions import get_metas
from datetime import datetime


bp = Blueprint('indicadores', __name__, url_prefix='/indicadores')


@bp.route('/indicador1', methods=['GET'])
@login_required
def indicador1():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'show_title': True,
        'show_filter': True,
        'show_date': False,
        'show_decimales': True,
        'show_year': True
    }
    return render_template('indicadores/indicador1.html', **args)


@bp.route('/indicador2', methods=['GET'])
@login_required
def indicador2():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'show_title': True,
        'show_filter': True,
        'show_date': False,
        'show_decimales': True,
        'show_year': True
    }
    meta = get_metas('indicador2', datetime.now().year)
    for i in meta['meta']:
        args[i['titulo']] = i['metas']
    return render_template('indicadores/indicador2.html', **args)


@bp.route('/indicador4', methods=['GET'])
@login_required
def indicador4():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'meta': get_metas('indicador4', datetime.now().year)['meta'],
        'show_title': True,
        'show_filter': True,
        'show_date': False,
        'show_decimales': True,
        'show_year': True
    }
    return render_template('indicadores/indicador4.html', **args)


@bp.route('/indicador5', methods=['GET'])
@login_required
def indicador5():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'meta': get_metas('indicador5', datetime.now().year)['meta'],
        'show_title': True,
        'show_filter': True,
        'show_date': True,
        'show_decimales': True,
        'show_year': False
    }
    return render_template('indicadores/indicador5.html', **args)


@bp.route('/indicador7', methods=['GET'])
@login_required
def indicador7():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'meta': 100,
        'show_title': True,
        'show_filter': False,
        'show_date': False,
        'show_decimales': True,
        'show_year': False
    }
    return render_template('indicadores/indicador7.html', **args)


@bp.route('/indicador8', methods=['GET'])
@login_required
def indicador8():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'show_title': True,
        'show_filter': False,
        'show_date': False,
        'show_decimales': True,
        'show_year': False
    }
    return render_template('indicadores/indicador8.html', **args)


@bp.route('/uso', methods=['GET'])
@login_required
def uso():
    args = {
        'year': datetime.now().year,
        'usuario': session['name'],
        'tiempo': session['last_login'],
        'rol': session['rol'],
        'show_title': True,
        'show_filter': False,
        'show_date': True,
        'show_decimales': True,
        'show_year': False
    }
    meta = get_metas('uso', datetime.now().year)
    for i in meta['meta']:
        args[i['titulo']] = i['meta']
    return render_template('indicadores/uso.html', **args)
