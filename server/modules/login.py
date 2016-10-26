# coding: utf-8
from flask import (Blueprint, url_for, redirect, request, session, flash)
from server.lib.gauth import GoogleAuth
import functools

module = Blueprint('login', __name__)


@module.route("/google_login")
def google_login():

    url = None
    print("inside google_login")

    try:
        url = GoogleAuth().authorized_url()
    except Exception as e:
        print("error:", e)
    return redirect(url)


@module.route("/oauth2callback")
def oauth2callback():
    google_auth = GoogleAuth()
    code = request.args['code']
    credentials = google_auth.create_credentials(code)
    email = google_auth.get_email(credentials)

    if not google_auth.validate_email(email):
        message = '「%s」は無効なアカウントです。@klab.comアカウントでログインしてください。' % email
        flash(message, 'error')
        return redirect(url_for('index'))

    session['user_email'] = email

    return redirect(url_for('top.index'))


def require_login(func):

    @functools.wraps(func)
    def wrapped(*args, **kw):

        if 'user_email' not in session:

            message = "ログインが必要です。"
            flash(message, 'error')

            return redirect(url_for('index'))
        return func(*args, **kw)
    return wrapped


@module.route("/logout", methods=['GET'])
@require_login
def logout():
    session.clear()
    req = request.values
    if "Connection" in req and req["Connection"] == "False":
            message = "接続が切断されました。再度ログインしてください。"
            flash(message, 'warning')
    return redirect(url_for('index'))
