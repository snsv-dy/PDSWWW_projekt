from flask import render_template
from flask_login import login_required
from app import app


@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')


