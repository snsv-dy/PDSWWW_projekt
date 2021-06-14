from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import app
from app.models import *
from app.email import send_email


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