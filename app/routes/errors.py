from flask import render_template
from app import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Żądana strona nie istnieje'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', message='Wystąpił błąd serwera'), 500


@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html', message='Brak autoryzacjia'), 401
