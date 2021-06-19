from flask import render_template, flash, redirect, url_for, request, session
from app import app
from app.models import *
from app.forms import BeforeTestForm
from datetime import datetime, timedelta


@app.route('/before_test/<int:term_id>', methods=['GET', 'POST'])
def before_test(term_id):
    # Generowanie id
    term = TestTerm.query.filter_by(id=term_id).first()
    if term is None:
        flash("Nie znaleziono terminu testu.")
        return redirect(url_for('index'))

    form = BeforeTestForm()
    if form.validate_on_submit():
        answer_obj = TestAnswer(email=form.email.data, full_name=form.name.data)
        term.answers.append(answer_obj)
        db.session.add(term)
        db.session.add(answer_obj)
        db.session.commit()
        session['answer_id'] = answer_obj.id
        end_time = datetime.now() + timedelta(minutes=term.test.time)
        session['end_time'] = int(end_time.timestamp() * 1000)

        flash('Test się rozpoczyna, powodzenia!', 'success')
        return redirect(url_for('quiz', number=1))

    return render_template('before_test.html', term=term, form=form)

def get_question_answer(answer_obj, index):
    answers = [answer for answer in answer_obj.answers if answer.question.nr == index+1]
    if answers:
        print(f"found answer for question {index}")
        return answers[0]
    return None

def time_exceeded(time):
    return time is None or int(datetime.now().timestamp() * 1000) >= time

@app.route('/test/<int:number>', methods=['GET', 'POST'])
def quiz(number):
    if session.get('answer_id') is None:
        # Tymczasowe przypisywanie odpowiedzi na test
        # powinno być ustawiwane przed testem.
        flash('Nie rozpoczęto testu.', 'error')
        return redirect('/')

    answer_obj = TestAnswer().query.filter_by(id=session['answer_id']).first()
    if answer_obj is None:
        # Prawdopodobnie jeszcze jest id z poprzedniej sesji i trzeba usunąć ciasteczko,
        # ale to zdarza się tylko po czyszczeniu bazy danych.
        del session['answer_id']
        return redirect(url_for('index'))  # zmień na strone główną.

    term_obj = TestTerm.query.filter_by(id=answer_obj.test_term_id).first()
    test_obj = Test.query.filter_by(id=term_obj.testid).first()

    print('answer ', answer_obj, answer_obj.id)
    if len(request.form) > 0:
        term = TestTerm.query.filter_by(id=answer_obj.test_term_id).first()
        test = Test.query.filter_by(id=term.testid).first()

        update_previous_question(request.form, answer_obj, test)

    if time_exceeded(session.get('end_time')):
        return redirect(url_for('summary', term_id=term_obj.id))

    if number == 0:
        # To też coś nie działa jak trzeba, po kliknięciu zakończ, odpowiedź pytania nie jest zapisywana.
        print('updating test')
        return redirect(url_for('summary', term_id=term_obj.id))

    questions = test_obj.questions

    if not questions:
        return redirect(url_for('summary', term_id=term_obj.id))

    number -= 1

    if number < 0 or number >= len(questions):
        number = 0

    question = questions[number]

    answer = get_question_answer(answer_obj, number)  # quiz.question_answers.get(number)

    if answer is not None:
        answer = answer.data
        
    return render_template('test.html', test_params=test_obj, question=question, anwsers=answer,
                           current_index=number + 1, answered_indexes=[a.nr - 1 for a in test_obj.questions if a.id in [k.question_id for k in answer_obj.answers if k.data is not None]],
                           end_time=session.get('end_time'))


def update_previous_question(form, answer_obj, test_obj):
    question_type = form.get('question_type')
    question_index = form.get('question_index')

    anwser = form.getlist('anwser')
    index = int(question_index) - 1

    print('Updating question', index)

    print(anwser, index)

    question_obj = get_question_answer(answer_obj, index)
    if question_obj is None:
        print(f'question obj is none, index {index}')
        question_obj = QuestionAnswer()
        print("Creating answer")
        test_obj.questions[index].answers.append(question_obj)
        answer_obj.answers.append(question_obj)

        db.session.add(test_obj.questions[index])
        db.session.add(test_obj)

    question_obj.data = None
    if question_type == '0' and len(anwser) > 0:
        question_obj.data = [int(i)-1 for i in anwser]
    elif question_type == '1' and len(anwser) > 0:
        print('Updating single choice question ---------------')
        print(int(anwser[0])-1)
        question_obj.data = int(anwser[0])-1
    elif question_type == '2' and len(anwser) > 0 and anwser[0] != '':
        question_obj.data = anwser[0]

    db.session.add(question_obj)
    db.session.add(answer_obj)
    db.session.commit()


@app.route('/summary/<int:term_id>')
def summary(term_id):
    if session.get('answer_id') is not None:
        del session['answer_id']
        del session['end_time']

    flash('Test zakończony', 'success')

    term = TestTerm.query.filter_by(id=term_id).first()

    if term is None:
        flash('Żądany termin nie istnieje', 'error')
        return redirect(url_for('index'))

    return render_template('summary.html', term=term)
