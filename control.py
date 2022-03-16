from flask import request
from datetime import datetime
from main import app
from db import db


@app.route('/app/getTotals', methods=['POST'])
def get_totals():
    if request.method == 'POST':
        years = int(request.form.get('year'))
        yeare = years + 1
    else:
        years = datetime.now().year
        yeare = years + 1
    labels = []
    activos = []
    noactivos = []
    totales = []
    colores_activos = []
    colores_noactivos = []
    colores = []
    cursor = db.cursor()
    cursor.execute(
        "SELECT Mes_filtro as mes, COUNT(CASE WHEN Bk_ContactoStatus = 'Activa' THEN Id_Asociado ELSE NULL END) as "
        "activas, COUNT(CASE WHEN Bk_ContactoStatus = 'No Activa' THEN Id_Asociado ELSE NULL END) as no_activas, "
        "COUNT(Id_Asociado) as total FROM asociados WHERE Bk_ContactoStatus != 'Moroso' AND date_base >= '%i-01-01 "
        "00:00:00' AND date_base < '%i-01-01 00:00:00' GROUP BY Mes_filtro ORDER BY date_base" % (
            years, yeare))
    for i in cursor:
        labels.append(i[0])
        activos.append(i[1])
        colores_activos.append('#89aadb')
        colores_noactivos.append('#fbb034')
        colores.append('#7ac143')
        noactivos.append(i[2])
        totales.append(i[3])
    return {'status': True, 'data': [activos, noactivos, totales], 'labels': labels,
            'colores': [colores_activos, colores_noactivos, colores]}
