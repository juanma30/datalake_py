from flask import (
    Blueprint, flash, g, request, session
)
from gs1.auth import login_required
from gs1.db import get_db
from gs1.functions import get_metas
from datetime import datetime

bp = Blueprint('app', __name__, url_prefix='/app')


@bp.route('/getTotals', methods=['POST'])
@login_required
def getTotals():
    db, c = get_db()
    filter = ''
    if request.method == 'POST':
        years = int(request.form.get('year'))
        yeare = years + 1
        region = request.form.get('region')
        tamanio = int(request.form.get('tamanio')) if request.form.get('tamanio') != 'all' else None
        segmentacion = request.form.get('segmentacion')
        industria = request.form.get('industria')
        if region != 'all':
            filter += f' and nielsen like "{region}%" '
        if tamanio is not None:
            filter += f' and Ramo like "%{tamanio}" '
        if segmentacion != 'all':
            filter += f' and segmento = "{segmentacion}" '
        if industria != 'all':
            filter += f' and industria = "{industria}" '
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
    c.execute(
        "SELECT Mes_filtro as mes, COUNT(CASE WHEN Bk_ContactoStatus = 'Activa' THEN Id_Asociado ELSE NULL END) as activas, "
        "COUNT(CASE WHEN Bk_ContactoStatus = 'No Activa' THEN Id_Asociado ELSE NULL END) as no_activas "
        "FROM info_asociados WHERE Bk_ContactoStatus != 'Moroso' AND "
        "date_base >= '%s-01-01 00:00:00' AND date_base < '%s-01-01 00:00:00' "+filter+" GROUP BY Mes_filtro ORDER BY date_base",
        (years, yeare)
    )
    listado = c.fetchall()
    for i in listado:
        labels.append(i['mes'])
        activos.append(i['activas'])
        colores_activos.append('#89aadb')
        colores_noactivos.append('#fbb034')
        colores.append('#7ac143')
        noactivos.append(i['no_activas'])
        totales.append(i['activas'] + i['no_activas'])
    return {'status': True, 'data': [activos, noactivos, totales], 'labels': labels,
            'colores': [colores_activos, colores_noactivos, colores]}


def check_ramo(ramo):
    niveles = {0: ['C0', 'T0', 'M0'],
               1: ['C1', 'T1', 'M1'],
               2: ['C2', 'T2', 'M2'],
               3: ['C3', 'T3', 'M3'],
               4: ['C4', 'T4', 'M4'],
               5: ['C5', 'T5', 'M5'],
               6: ['C6', 'T6', 'M6'],
               7: ['C7', 'T7', 'M7'],
               8: ['C8', 'T8', 'M8', 'F8'],
               9: ['C9', 'T9', 'M9'],
               10: ['C10', 'D10', 'F10', 'T10', 'M10'],
               11: ['C11', 'D11', 'T11', 'M11'],
               'LEI': ['LEI'],
               'Otros': ['CD', 'FE', 'NA', 'NB', 'NC', 'RUP']}

    for i in niveles:
        if ramo in niveles[i]:
            return i

    return None


@bp.route('/retenciones', methods=['POST'])
@login_required
def retenciones():
    db, c = get_db()
    data = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {},9: {}, 10: {}, 11: {}, 'LEI': {}, 'Otros': {}}
    mes = datetime.now().month - 1 if datetime.now().month > 1 else 11
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
             "Noviembre", "Diciembre"]
    year = datetime.now().year
    filter = ''
    if request.method == 'POST':
        year = request.form.get('year')
        region = request.form.get('region')
        segmentacion = request.form.get('segmentacion')
        industria = request.form.get('industria')
        if region != 'all':
            filter += " and nielsen = '{}' ".format(region)
        if segmentacion != 'all':
            filter += " and segmento = '{}' ".format(segmentacion)
        if industria != 'all':
            filter += " and industria = '{}' ".format(industria)
    c.execute(
        "select * from retencion where year = %s"+filter,
        (year,)
    )

    rs = c.fetchall()

    for i in rs:
        ramo = check_ramo(i['Ramo'])
        if ramo is not None:
            if 0 not in data[ramo].keys():
                data[ramo][0] = 1
            else:
                data[ramo][0] += 1
            contador = 1
            for m in meses:
                if contador > mes:
                    break
                if i[f'Estatus{m}'] == 'Activa':
                    r = check_ramo(i[f'Ramo{m}'])
                    if r is not None:
                        if contador not in data[r].keys():
                            data[r][contador] = 1
                        else:
                            data[r][contador] += 1
                contador += 1

    return {'status': True, 'data': [data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data['LEI'], data['Otros']]}


@bp.route('/inscripciones', methods=['POST'])
@login_required
def inscripciones():
    db, c = get_db()
    if request.method == 'POST':
        years = int(request.form.get('year'))
        region = request.form.get('region')
        tamanio = int(request.form.get('tamanio')) if request.form.get('tamanio') != 'all' else None
        segmentacion = request.form.get('segmentacion')
        industria = request.form.get('industria')
        filter = ''
        if region != 'all':
            filter += f' and region like "{region}%" '
        if tamanio is not None:
            filter += f' and tamanio like "%{tamanio}" '
        if segmentacion != 'all':
            filter += f' and marketing = "{segmentacion}" '
        if industria != 'all':
            filter += f' and industria = "{industria}" '
        c.execute(
            "select month(fecha) as mes, count(distinct numero_asociado) as total from ind2_catalogo "
            "where fecha between '%s-01-01 00:00:00' and '%s-12-31 23:59:59' " + filter + " group by month(fecha)",
            (years, years)
        )
        catalogo = c.fetchall()

        c.execute(
            "select month(fecha) as mes, "
            "count(distinct (case when codigo like 'INS010001%' and tamanio like 'C%' then numero_asociado end)) as cadenas, "
            "count(distinct (case when codigo like 'INS010047%' then numero_asociado end)) as gln, "
            "count(distinct numero_asociado) as total "
            "from ind2_codigo where fecha between '%s-01-01 00:00:00' and '%s-12-31 23:59:59' " + filter + " group by month(fecha)",
            (years, years)
        )
        codigo = c.fetchall()

        c.execute(
            "select month(fecha) as mes, count(distinct numero_asociado) as total from ind2_lei "
            "where fecha between '%s-01-01 00:00:00' and '%s-12-31 23:59:59' " + filter + " group by month(fecha)",
            (years, years)
        )
        lei = c.fetchall()
        return {'status': True, 'data': {'catalogo': catalogo, 'codigo': codigo, 'lei': lei}}
    else:
        return {'status': False, 'data': {'catalogo': 0, 'codigo': 0, 'lei': 0}}


@bp.route('/getInd4', methods=['POST'])
@login_required
def getIndicador4():
    if request.method == 'POST':
        db, c = get_db()
        date_start = f'{request.form.get("year")}-01-01 00:00:00'
        date_end = f'{request.form.get("year")}-12-31 23:59:59'
        region = request.form.get('region')
        tamanio = int(request.form.get('tamanio')) if request.form.get('tamanio') != 'all' else None
        segmentacion = request.form.get('segmentacion')
        industria = request.form.get('industria')
        filter = ''
        if region != 'all':
            filter += f' and region like "{region}%" '
        if tamanio is not None:
            filter += f' and tamanio like "%{tamanio}" '
        if segmentacion != 'all':
            filter += f' and marketing = "{segmentacion}" '
        if industria != 'all':
            filter += f' and industria = "{industria}" '
        c.execute(
            "select count(distinct numero_asociado) as total from ind4 "
            "where fecha >= %s and fecha <= %s " + filter,
            (date_start, date_end)
        )
        total = c.fetchone()
        return {'status': True, 'data': total['total']}
    else:
        return {'status': False, 'data': 0}


@bp.route('/getIndicador7', methods=['POST'])
@login_required
def getIndicador7():
    if request.method == 'POST':
        db, c = get_db()
        if request.form.get("year") is not None:
            date_start = f'{request.form.get("year")}-01-01 00:00:00'
            date_end = f'{request.form.get("year")}-12-31 23:59:59'
        else:
            date_start = f'{datetime.now().year}-01-01 00:00:00'
            date_end = f'{datetime.now().year}-12-31 23:59:59'
        c.execute(
            "select date_format(from_unixtime(createdtime/1000),'%m') as Mes,"
            "count(workorderid) as totales,sum(case when statusname = 'Open' then 1 else 0 end) as abiertos,"
            "sum(case when statusname = 'Closed' or statusname = 'Resolved' or statusname = 'Cancelled N/A' then 1 else 0 end) as cerrados,"
            "sum(case when statusname = 'Resolved' then 1 else 0 end) as resueltos "
            "from indicador7 where priorityname not in ('5) Operación Interna','6) Solicitudes Desarrollo','7) Procedimientos de Seguridad') "
            "and from_unixtime(createdtime/1000) between %s and %s "
            "group by month(from_unixtime(createdtime/1000))",
            (date_start, date_end)
        )
        data = c.fetchall()
        return {'status': True, 'data': data}
    return {'status': False, 'data': 0}


@bp.route('/getIndicador8', methods=['POST'])
@login_required
def getIndicador8():
    if request.method == 'POST':
        db, c = get_db()
        year = request.form.get('year') if request.form.get('year') is not None else datetime.now().year
        c.execute(
            "select * from indicador8 where Year = %s",
            (year,)
        )
        data = c.fetchall()
        return {'status': True, 'data': data}
    return {'status': False, 'data': 0}


@bp.route('/getIndicador5', methods=['POST'])
@login_required
def getIndicador5():
    year = datetime.now().year
    dateStart = None
    dateEnd = None
    data = {'totales': 0, 'nuevos': 0}
    if request.method == 'POST':
        year = int(request.form.get('year'))
        dateStart = request.form.get('date-start') + ' 00:00:00'
        dateEnd = request.form.get('date-end') + ' 23:59:59'
    if dateStart is None:
        dateStart = "{}-01-01 00:00:00".format(year - 2)
        dateEnd = "{}-12-31 23:59:59".format(year)
    db, c = get_db()
    c.execute(
        "select count(case when fecha <= %s then gln_gtin_mercado end) as totales, "
        "count(distinct case when fecha between %s and %s then gln_gtin_mercado end) as nuevos "
        "from ind5",
        (dateEnd, dateStart, dateEnd)
    )
    rs = c.fetchall()
    if len(rs) > 0:
        return {'status': True, 'data': {'totales': rs[0]['totales'], 'nuevos': rs[0]['nuevos']}}
    return {'status': True, 'data': data}


@bp.route('/getMeta', methods=['POST'])
@login_required
def getMeta():
    if request.method != 'POST':
        return {'status': False, 'data': None}
    indicador = request.form.get('indicador')
    anio = request.form.get('anio')
    meta = get_metas(indicador, anio)
    return {'status': True, 'data': meta['meta']}


@bp.route('/cursos', methods=['POST'])
@login_required
def cursos():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct numero_asociado) as total from cursos '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/eventos', methods=['POST'])
@login_required
def eventos():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct numero_asociado) as total from eventos '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/asesorias', methods=['POST'])
@login_required
def asesorias():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct id_solicitud) as total from asesorias '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/desabasto', methods=['POST'])
@login_required
def desabasto():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct numero_asociado) as total from desabasto '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/secodat', methods=['POST'])
@login_required
def secodat():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct numero_asociado) as total from hada '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/infocode', methods=['POST'])
@login_required
def infocode():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct numero_asociado) as total from infocode '
        'where fecha between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/catalogo', methods=['POST'])
@login_required
def catalogo():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct Id_Asociado) as total from info_asociados '
        'where Catálogo = "Activa" and date_base between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/codigo', methods=['POST'])
@login_required
def codigo():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct Id_Asociado) as total from info_asociados '
        'where Estandar = "Activa" and date_base between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}


@bp.route('/lei', methods=['POST'])
@login_required
def lei():
    filter = ''
    if request.method != 'POST':
        return {'status': False, 'data': None}
    db, c = get_db()
    ds = request.form.get('date-start')+' 00:00:00'
    de = request.form.get('date-end')+' 23:59:59'
    c.execute(
        'select count(distinct Id_Asociado) as total from info_asociados '
        'where LEI = "Activa" and date_base between %s and %s '+filter,
        (ds, de)
    )
    data = c.fetchone()
    return {'status': True, 'data': data['total']}
