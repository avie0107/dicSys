from flask import (Blueprint, render_template)

module = Blueprint('/', __name__)


@module.route("/")
def index():
    return 'hello'
