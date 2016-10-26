# coding: utf-8
from flask import (Blueprint, render_template, session)
from server.modules.login import require_login

module = Blueprint('top', __name__)


@module.route("/", methods=['POST', 'GET'])
@require_login
def index():
    email = None
    if 'user_email' in session:
        email = session['user_email']
    return render_template('top.html', user_email=email)
