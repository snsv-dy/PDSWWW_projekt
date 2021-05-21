from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.sample_data import sample_test, sample_anwsers
from app.models import Teacher
from app.util import display_form_errors


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
        teacher = Teacher.query.filter_by(email=form.email.data.lower()).first()
        if teacher is None:
            flash('Podany email nie jest zarejestrowany', 'error')
            return render_template('login.html', form=form)
        if teacher.verify_password(form.password.data):
            login_user(teacher, remember=form.remember_me.data)
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('index'))
        flash('Niepoprawne hasło', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        teacher = Teacher(email=form.email.data.lower(), password=form.password.data)
        db.session.add(teacher)
        db.session.commit()
        flash('Zostałeś pomyślnie zarejestrowany!', 'success')
        return redirect(url_for('index'))
    display_form_errors(form)
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    flash('Zostałeś pomyślnie wylogowany', 'success')
    logout_user()
    return redirect(url_for('index'))


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
