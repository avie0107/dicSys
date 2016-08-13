# coding: utf-8
from flask import (Blueprint, render_template, session)

module = Blueprint('search', __name__)


@module.route("/", methods=['POST', 'GET'])
def index():
    return render_template("search.html")

