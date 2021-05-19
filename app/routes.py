from flask import render_template, flash
from app import app, db
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    # u = User(username='susan', email='susan@example.com')
    # db.session.add(u)
    # db.session.commit()
    # flash('Example success notification!', 'success')
    # flash('Example error notification!', 'error')
    # flash('Example warning notification!', 'warning!')
    return render_template('manage.html')
