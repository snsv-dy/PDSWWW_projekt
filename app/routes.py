from flask import render_template, flash
from app import app, db
from app.models import User


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

@app.route('/test/<int:index>')
def quiz(index=1):
	questions = [
		{
			'index': 1,
			'type': 0,
			'content': 'aaa',
			'anwsers': [
				'a',
				'b'
			],
			'images': [
				'baked_salmon.webp',
				'jupiter.jpg'
			],
			'points': 2
		},
		{
			'index': 2,
			'type': 1,
			'content': 'Co jest cięższe?',
			'anwsers': [
				'1kg piór',
				'1kg stali'
			],
			'points': 2
		},
		{
			'index': 3,
			'type': 2,
			'content': 'Chjian',
			'images': [
				'jupiter.jpg'
			],
			'points': 2
		}
	]

	test_params = {
		'title': 'tytuł',
		'author': 'autor',
		'questions': questions,
		'number_of_questions': len(questions)
	}

	index -= 1

	if index < 0 or index >= len(questions):
		index = 0

	question = questions[index]

	return render_template('test.html', test_params=test_params, question=question)