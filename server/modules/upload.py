# coding: utf-8
from flask import (Blueprint, render_template, request, flash)
from openpyxl import load_workbook
import os
module = Blueprint('upload', __name__)


@module.route("/", methods=['POST', 'GET'])
def index():
    return render_template("upload.html")


@module.route("/read", methods=['POST', 'GET'])
def read_file():
    """

    """
    file=None
    form = request.form
    if request.files['file'].filename == '':
        message = 'アップロードファイルがありません。'
        flash(message, 'warning')
        print(message)
        #raise Exception

    else:
        file = request.files['file']

    # TODO: check file extension
    """ root, ext = os.path.splitext(file)

    if ext != '.xlsx':
        message = 'アップロードしたファイルの拡張子がxlsxではないです。'
        flash(message, 'warning')
        #raise Exception
        print(message)"""

    # TODO: path+filename
    print(file.filename)
    file.save(file.filename)
    wb = load_workbook(file)
    print(wb.get_sheet_names())
    for ws in wb.get_sheet_names():
        sheet_ranges = wb[ws]
        print(sheet_ranges['A5'].value)
        """if ws == "Set Phrases":
          for row in wb[ws].rows:
                for cell in row:
                    if cell.value != "None" or cell.value is not None:
                        print(cell.coordinate, cell.value)"""

    return 'saved'
