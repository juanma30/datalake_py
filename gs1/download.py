from flask import (
    Blueprint, flash, g, request, session
)
from gs1.auth import login_required
from gs1.db import get_db
from gs1.functions import initExcel, addContent, closeExcel
from datetime import datetime

bp = Blueprint('download', __name__, url_prefix='/download')


@bp.route('/base_asociados', methods=['POST'])
@login_required
def base_asociados():
    db, c = get_db()
    ds = '2022-01-01 00:00:00'
    de = '2022-12-31 23:59:59'
    Mes_filtro = 'Enero'
    c.execute(
        'select Concepto, Id_Asociado, RazonSocial, RFC, Region, Estado, Ramo, Cliente,'
        'Tipo_General, Cartera, Giro, Sector, Aniversario, Año, Mes, EMAIL, Direccion,'
        'NumExterior, NumInterior, Colonia, Ciudad, CP, Bc_CorreoEmpresa, At_RefBancaria,'
        'Bk_Contacto, Bc_Nombre, Bc_A_Paterno, Bc_A_Materno, Bc_Titulo, Bc_telefono,'
        'Bc_Correo, Bk_Etiqueta, Bc_Etiqueta, Bk_ContactoStatus, At_OrdenRAsociados,'
        'Estandar, Catálogo, LEI, Base from info_asociados '
        'where date_base between %s and %s and Mes_filtro = %s',
        (ds, de, Mes_filtro)
    )
    data = c.fetchall()
