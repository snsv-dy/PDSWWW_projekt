from flask import render_template, flash
from app import app, db
from app.models import User
from app.sample_data import sample_test, sample_anwsers


@app.route('/')
@app.route('/index')
def index():
    # u = User(username='susan', email='susan@example.com')
    # db.session.add(u)
    # db.session.commit()
    flash('Example success notification!', 'success')
    flash('Example error notification!', 'error')
    flash('Example warning notification!', 'warning!')
    return render_template('index.html')

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