from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app
from app.models import *


@app.route('/manage')
@login_required
def manage():
    teacher = current_user
    tests = teacher.tests
    return render_template('manage.html', tests=tests)


@app.route('/details/<int:test_id>')
@login_required
def details(test_id):
    test = Test.query.filter_by(id=test_id).first()

    if test is None:
        flash('Żądany test nie istnieje', 'error')
        return redirect(url_for('index'))

    if test.teacherid != current_user.id:
        flash('Nie jesteś uprawiony do wglądu w żądany test', 'error')
        return redirect(url_for('index'))

    return render_template('details.html', test=test)


