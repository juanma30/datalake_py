from flask import render_template, url_for
from main import app
from datetime import datetime


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/indicador1')
def indicador1():
    anio = datetime.now()
    return render_template('indicador1.html', year=anio.year)

@app.route('/indicador2')
def indicador2():
    return render_template('indicador2.html')
