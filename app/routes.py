from flask import render_template, flash
from app import app, db
from app.forms import LoginForm
from app.models import User
from app.sample_data import sample_test, sample_anwsers


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/manage')
def manage():
    return render_template('manage.html')

@app.route('/before_test')
def before_test():
    return render_template('before_test.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Zalogowano pomyślnie!', 'success')
    return render_template('login.html', form=form)
@app.route('/test_review')
def quiz_review():
	return render_template('test_review.html', test_params=sample_anwsers)

@app.route('/test_edit/<int:index>')
def quiz_edit(index=1):

	index -= 1

	questions = sample_test['questions']

	if index < 0 or index >= len(questions):
		index = 0

	question = questions[index]

	return render_template('test_edit.html', test_params=sample_test, question=question)

@app.route('/test/<int:index>')
def quiz(index=1):

	questions = sample_test['questions']

	index -= 1

	if index < 0 or index >= len(questions):
		index = 0

	question = questions[index]

	return render_template('test.html', test_params=sample_test, question=question)
