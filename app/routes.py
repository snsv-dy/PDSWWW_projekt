from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.sample_data import sample_test, sample_anwsers
from app.models import *
from app.util import display_form_errors
from app.email import send_email


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Żądana strona nie istnieje'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', message='Wystąpił błąd serwera'), 500


@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html', message='Brak autoryzacjia'), 401


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def index_post():
    try:
        code = int(request.form.get('code'))
    except ValueError:
        code = 0

    term = TestTerm.query.filter_by(code=code).first()

    if term is None:
        flash('Podany kod jest niepoprawny', 'error')
        return redirect(url_for('index'))

    flash('Podany kod jest poprawny', 'success')
    return redirect(url_for('before_test', term_id=term.id))


@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')


@app.route('/before_test/<int:term_id>')
def before_test(term_id):
    # TODO: Można by na tej stronie dodać pole do podania nazwiska i adresu email (Chyba że na stronie głównej)

    # Generowanie id
    term = TestTerm.query.filter_by(id=term_id).first()
    if term is None:
        flash("Nie znaleziono terminu testu.")
        return redirect(url_for('index'))

    answer_obj = TestAnswer(email='emal@yeah.coc', full_name='empty hand')
    term.answers.append(answer_obj)
    db.session.add(term)
    db.session.add(answer_obj)
    db.session.commit()
    session['answer_id'] = answer_obj.id

    return render_template('before_test.html', id=answer_obj.id)


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

            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('manage')
            return redirect(next)

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


@app.route('/review/<int:term_id>/<int:answer_nr>')
@login_required
def quiz_review(term_id, answer_nr):
    term = TestTerm.query.filter_by(id=term_id).first()

    if term is None:
        flash('Nieprawidłowy termin testu', 'error')
        return redirect(url_for('index'))

    if answer_nr > len(term.answers) or answer_nr <= 0:
        flash('Nie ma takiej pracy do sprawdzenia', 'error')
        return redirect(url_for('index'))

    answer = term.answers[answer_nr-1]
    return render_template('test_review.html', answer=answer, answer_nr=answer_nr, term_id=term_id, calc_points=calc_points)


def calc_points(question_answer):
    qa = question_answer

    if qa.question.type == Question.SINGLE_CHOICE:
        correct = qa.question.data['correct']
        provided = qa.data
        return qa.question.points if provided == correct else 0

    if qa.question.type == Question.MULTIPLE_CHOICE:
        correct = qa.question.data['correct']
        provided = qa.data

        points_per_option = qa.question.points / len(correct)
        print(correct, provided)
        points = 0
        for option in provided:
            if option in correct:
                points += points_per_option
            else:
                points -= points_per_option

        points = max(points, 0)
        points = round(points * 2) / 2
        return points

    if qa.question.type == Question.OPEN:
        return 0


@app.route('/review/<int:term_id>/<int:answer_nr>', methods=['POST'])
@login_required
def quiz_review_post(term_id, answer_nr):
    term = TestTerm.query.filter_by(id=term_id).first()

    if term is None:
        flash('Nieprawidłowy termin testu', 'error')
        return redirect(url_for('index'))

    if answer_nr > len(term.answers) or answer_nr <= 0:
        flash('Nie ma takiej pracy do sprawdzenia', 'error')
        return redirect(url_for('index'))

    answer = term.answers[answer_nr - 1]

    valid = True

    points = {}
    grade = 0

    form = request.form
    try:
        for field in form.keys():
            if field == 'grade':
                grade = float(form['grade'])
                if 1 < grade > 5:
                    valid = False
                    break
            else:
                question_nr = int(field)
                max_points = answer.answers[question_nr-1].question.points
                provided_points = float(form[field])
                points[question_nr] = provided_points
                if provided_points > max_points:
                    valid = False
                    break
    except ValueError:
        valid = False

    if not valid:
        flash('Niepoprawne dane', 'error')
        return redirect(url_for('quiz_review', term_id=term_id, answer_nr=answer_nr))

    scored_points = sum(points.values())
    max_points = sum([answer.question.points for answer in answer.answers])

    send_email('social.insight.noreply@gmail.com', 'Wyniki', 'test_result', grade=grade, points=points, answer=answer,
               scored_points=scored_points, max_points=max_points)

    db.session.delete(answer)
    db.session.commit()

    next_answer_nr = answer_nr
    if next_answer_nr > len(term.answers):
        next_answer_nr -= 1

    if next_answer_nr == 0:
        flash('Wszystkie testy w tym terminie zostały już sprawdzone', 'success')
        return redirect(url_for('manage'))

    return redirect(url_for('quiz_review', term_id=term_id, answer_nr=next_answer_nr))


# sample_test['questions'][0]['anwsers'].append('hehe')
# question_anwsers = [[1, 3], 2, 'Siema']

# @app.route('/edit/structure/<action>/<param>', methods=['GET', 'POST'])
def quiz_edit_structure(action, param, test_obj):
    print('quiz edit', test_obj)
    if action == 'add_question' and param in ['0', '1', '2']:
        question = Question(type=int(param), question='', points=1.0, data=None, nr=len(test_obj.questions))

        if param in ['0', '1']:
            data = {'all': [], 'correct': []}

        test_obj.questions.append(question)
        db.session.add(question)
        db.session.add(test_obj)
        db.session.commit()
        print('test questions AAAA', test_obj.questions)
        return redirect('/edit/' + str(test_obj.id) + '/' + str(len(test_obj.questions)))
    elif action == 'remove_question':
        print('yeee')
        index = int(param) - 1

        # To na dole nie działa, i pytania nie są usuwane z bazy danych.
        # Question.query.filter_by(id=test_obj.questions[index].id).delete()
        del test_obj.questions[index]
        db.session.add(test_obj)
        db.session.commit()
        return redirect('/edit/' + str(index))

def update_test_question(form, test_obj):
    print(form)
    question_index = form.get('question_index')
    index = int(question_index) - 1
    question_type = form.get('question_type')

    title = form.get('title')
    points = form.get('points')
    question_content = form.get('question')

    print('index', index, 'rest', title, points, question_content)

    test_obj.title = title
    question = test_obj.questions[index]
    question.points = float(points)
    question.question = question_content

    if question_type in ['0', '1']:
        answers = form.getlist('anwser_text')
        correct_answers = form.getlist('answer')

        question.data = {}
        question.data['all'] = answers
        question.data['correct'] = [ int(i) for i in correct_answers ]
        if question_type == '1' and len(question.data['correct']) == 1:
            question.data['correct'] = question.data['correct'][0]

    db.session.add(test_obj)
    db.session.add(question)
    db.session.commit()
    db.session.flush()

# @login_required
@app.route('/edit/<int:test_id>')
@app.route('/edit/<int:test_id>/<int:number>', methods=['POST', 'GET'])
@app.route('/edit/<int:test_id>/-1/<action>/<param>', methods=['GET', 'POST'])
def quiz_edit(test_id=None, number=None, action=None, param=None):
    if test_id == None:
        flash('Nieznany test.', 'error')
        return redirect(url_for('/manage'))

    test = Test.query.filter_by(id=test_id).first()

    if len(request.form) > 0:
        update_test_question(request.form, test)

    if action is not None and param is not None:
        return quiz_edit_structure(action, param, test)

    if number is None:
        return redirect('/edit/1/1')

    # if quiz_edit.Test is None:
    #     quiz_edit.Test = Test.query.filter_by(id=1).first()

    number -= 1
    questions = test.questions

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    # print('eeee', question.data['correct'])
    return render_template('test_edit.html', test_params=test, question=question, number_of_questions=len(test.questions), current_index=number + 1)

def update_previous_question(form, answer_obj, test_obj):
    question_type = form.get('question_type')
    question_index = form.get('question_index')

    anwser = form.getlist('anwser')
    index = int(question_index) - 1

    print(anwser, index)

    question_obj = None
    if index < len(answer_obj.answers):
        question_obj = answer_obj.answers[index]
    else:
        question_obj = QuestionAnswer()
        answer_obj.answers.append(question_obj)
        test_obj.questions[index].answers.append(question_obj)

        db.session.add(test_obj.questions[index])
        db.session.add(test_obj)

    if question_type == '0' and len(anwser) > 0:
        question_obj.data = [int(i) for i in anwser]
    elif question_type == '1' and len(anwser) > 0:
        question_obj.data = int(anwser[0])
    elif question_type == '2' and len(anwser) > 0:
        question_obj.data = anwser[0]

    db.session.add(question_obj)
    db.session.add(answer_obj)
    db.session.commit()


@app.route('/test_finish')
def quiz_end():
    if session.get('answer_id') is not None:
        answer_obj = TestAnswer().query.filter_by(id=session['answer_id']).first()
        del session['answer_id']
    return redirect('/test_summary')


@app.route('/test/', defaults={'number': 1})
@app.route('/test/<int:number>', methods=['GET', 'POST'])
def quiz(number):
    print('quiz-1', number)
    if session.get('answer_id') is None:
        # Tymczasowe przypisywanie odpowiedzi na test
        # powinno być ustawiwane przed testem.
        flash('Nie rozpoczęto testu.', 'error')
        return redirect('/')
    
    print('session: ', session.get('answer_id'))
    answer_obj = TestAnswer().query.filter_by(id=session['answer_id']).first()
    if answer_obj is None:
        # Prawdopodobnie jeszcze jest id z poprzedniej sesji i trzeba usunąć ciasteczko,
        # ale to zdarza się tylko po czyszczeniu bazy danych.
        del session['answer_id']
        return redirect(url_for('index')) # zmień na strone główną.

    print('answer ', answer_obj, answer_obj.id)
    if len(request.form) > 0:
        term = TestTerm.query.filter_by(id=answer_obj.test_term_id).first()
        test = Test.query.filter_by(id=term.testid).first()

        update_previous_question(request.form, answer_obj, test)

    if number == 0:
        # To też coś nie działa jak trzeba, po kliknięciu zakończ, odpowiedź pytania nie jest zapisywana.
        print('updating test')
        return redirect('/test_finish')

    term_obj = TestTerm.query.filter_by(id=answer_obj.test_term_id).first()
    test_obj = Test.query.filter_by(id=term_obj.testid).first()
    
    questions = test_obj.questions
    number -= 1

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]
    
    answer = None #quiz.question_answers.get(number) 
    # if answer:
    if len(answer_obj.answers) > number:
        answer = answer_obj.answers[number].data
    print(answer)
    return render_template('test.html', test_params=test_obj, question=question, anwsers=answer, current_index=number + 1)

@app.route('/test_summary')
def test_summary():
    return render_template('test_summary.html')
