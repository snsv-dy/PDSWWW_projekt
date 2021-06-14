from flask import render_template
from flask_login import login_required
from app import app


@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')


@app.route('/details/<int:test_id>')
@login_required
def details(test_id):
    return render_template('details.html')


