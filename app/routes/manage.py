from flask import render_template
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
    return render_template('details.html')


