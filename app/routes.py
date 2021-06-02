from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.sample_data import sample_test, sample_anwsers
from app.models import *
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


@app.route('/test_review/<int:term_id>/<int:answer_nr>')
def quiz_review(term_id, answer_nr):
    term = TestTerm.query.filter_by(id=term_id).first()

    if term is None:
        flash('Invalid test term', 'error')
        return redirect(url_for('index'))

    if answer_nr > len(term.answers) or answer_nr <= 0:
        flash('There is not tests to review', 'success')
        return redirect(url_for('index'))

    answer = term.answers[answer_nr-1]
    return render_template('test_review.html', answer=answer, answer_nr=answer_nr, term_id=term_id)


@app.route('/test_review/<answer_id>', methods=['POST'])
def quiz_review_post(answer_id):
    answer = TestAnswer.query.filter_by(id=answer_id).first()

    valid = True

    form = request.form
    try:
        for field in form.keys():
            if field == 'grade':
                if 1 < float(form['grade']) > 5:
                    valid = False
                    break
            else:
                question_nr = int(field)
                max_points = answer.answers[question_nr-1].question.points
                provided_points = float(form[field])
                if provided_points > max_points:
                    valid = False
                    break
    except ValueError:
        valid = False

    flash('Niepoprawne dane ' + str(valid), 'error')
    return redirect(url_for('quiz_review', answer_id=answer_id))


sample_test['questions'][0]['anwsers'].append('hehe')
question_anwsers = [[1, 3], 2, 'Siema']


def update_test_question(form):
    print(form)
    question_index = form.get('question_index')
    index = int(question_index) - 1
    question_type = form.get('question_type')

    title = form.get('title')
    points = form.get('points')
    question_content = form.get('question')

    print('index', index, 'rest', title, points, question_content)

    sample_test['title'] = title
    question = sample_test['questions'][index]
    question['points'] = int(points)
    question['content'] = question_content

    if question_type in ['0', '1']:
        anwsers = form.getlist('anwser_text')
        question['anwsers'] = anwsers


@app.route('/test_edit/structure/<action>/<param>', methods=['GET', 'POST'])
def quiz_edit_structure(action, param):
    print('number_of_questions', sample_test['number_of_questions'])
    if action == 'add_question' and param in ['0', '1', '2']:
        questions = sample_test['questions']
        n_questions = len(questions)
        question = {
            'index': n_questions + 1,
            'type': int(param),
            'content': '',
            'points': 1
        }

        if param in ['0', '1']:
            question['anwsers'] = []

        sample_test['questions'].append(question)
        sample_test['number_of_questions'] += 1
        print(sample_test['questions'])
        return redirect('/test_edit/' + str(n_questions + 1))
    elif action == 'remove_question':
        print('yeee')
        index = int(param) - 1

        n_questions = sample_test['number_of_questions']

        for i in range(index, n_questions):
            sample_test['questions'][i]['index'] -= 1

        del sample_test['questions'][index]
        sample_test['number_of_questions'] -= 1
        return redirect('/test_edit/' + str(index))


@app.route('/test_edit/')
@app.route('/test_edit/<int:number>', methods=['POST', 'GET'])
def quiz_edit(number=1):
    if len(request.form) > 0:
        update_test_question(request.form)

    number -= 1
    questions = sample_test['questions']

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    return render_template('test_edit.html', test_params=sample_test, question=question)


def update_previous_question(form):
    question_type = form.get('question_type')
    question_index = form.get('question_index')

    anwser = form.getlist('anwser')
    index = int(question_index) - 1

    print(anwser, index)

    if question_type == '0':
        question_anwsers[index] = [int(i) for i in anwser]
    elif question_type == '1':
        question_anwsers[index] = int(anwser[0])
    else:
        question_anwsers[index] = anwser[0]


@app.route('/test/')
@app.route('/test/<int:number>', methods=['GET', 'POST'])
def quiz(number=1):
    if len(request.form) > 0:
        update_previous_question(request.form)

    questions = sample_test['questions']
    number -= 1

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    anwser = question_anwsers[number]
    return render_template('test.html', test_params=sample_test, question=question, anwsers=anwser)


@app.route('/test_summary')
def test_summary():
    return render_template('test_summary.html')
