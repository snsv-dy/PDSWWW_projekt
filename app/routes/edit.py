from flask import render_template, flash, redirect, url_for, request
from app import app
from app.models import *


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



