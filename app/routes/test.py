from flask import render_template, flash, redirect, url_for, request, session
from app import app
from app.models import *


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
        return redirect(url_for('index'))  # zmień na strone główną.

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

    answer = None  # quiz.question_answers.get(number)
    # if answer:
    if len(answer_obj.answers) > number:
        answer = answer_obj.answers[number].data
    print(answer)
    return render_template('test.html', test_params=test_obj, question=question, anwsers=answer,
                           current_index=number + 1)


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


@app.route('/test_summary')
def test_summary():
    return render_template('test_summary.html')