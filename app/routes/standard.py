from flask import render_template, flash, redirect, url_for, request
from app import app
from app.models import *


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def index_post():
    try:
        code = int(request.form.get('code'))
    except ValueError:
        code = 0

    term = TestTerm.query.filter_by(code=code).first()

    if term is None:
        flash('Podany kod jest niepoprawny', 'error')
        return redirect(url_for('index'))

    flash('Podany kod jest poprawny', 'success')
    return redirect(url_for('before_test', term_id=term.id))


