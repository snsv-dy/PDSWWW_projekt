from flask import render_template, flash
from app import app, db
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/manage')
def manage():
    return render_template('manage.html')
