import json
import xlsxwriter
import os
from gs1.db import get_db


def get_metas(indicador, anio):
    db, c = get_db()

    if indicador is None:
        return None
    if anio is None:
        return None
    c.execute(
        "select meta from metas where indicador = %s and anio = %s",
        (indicador, anio)
    )
    meta = c.fetchone()
    return json.loads(meta['meta'])


def initExcel(nameFile):
    if nameFile is None:
        return None
    path = os.path.realpath('file')
    pathfile = "{}/{}".format(path, nameFile)
    return xlsxwriter.Workbook(pathfile)


def addContent(workbook, data, init_row=0):
    if workbook is None:
        return None
    sheet = workbook.add_worksheet()
    if len(data) > 0:
        total_row = len(data)
        total_col = len(data[0])
        index_row = 0
        for row in range(init_row, total_row):
            for col in range(0, total_col):
                sheet.write(row, col, data[index_row][col])
            index_row += 1
        return True
    return False


def closeExcel(workbook):
    if workbook is not None:
        workbook.close()
