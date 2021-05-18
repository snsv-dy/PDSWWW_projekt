from flask import render_template
from app import app, db
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    # u = User(username='susan', email='susan@example.com')
    # db.session.add(u)
    # db.session.commit()

    user = {'username': 'Jacek'}
    return render_template('index.html')
