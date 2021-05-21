from flask import render_template, flash
from app import app
from app.forms import LoginForm
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


@app.route('/test_edit/<int:number>')
def quiz_edit(number=1):
    number -= 1
    questions = sample_test['questions']

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    return render_template('test_edit.html', test_params=sample_test, question=question)


@app.route('/test/<int:number>')
def quiz(number=1):
    questions = sample_test['questions']
    number -= 1

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    return render_template('test.html', test_params=sample_test, question=question)


@app.route('/test_summary')
def test_summary():
    return render_template('test_summary.html')
