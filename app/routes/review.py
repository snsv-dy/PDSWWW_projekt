from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import app
from app.models import *
from app.util import *
from app.email import send_email


@app.route('/review/term/<int:term_id>')
@login_required
def review_term(term_id):
    check_res = check_term(term_id=term_id)
    if check_res is not None: return check_res

    term = TestTerm.query.filter_by(id=term_id).first()

    if not term.not_reviewed_answers:
        flash('Nie ma więcej prac do sprawdzenia', 'success')
        return redirect(url_for('details', test_id=term.test.id))

    return redirect(url_for('review_answer', answer_id=term.not_reviewed_answers[0].id))


@app.route('/review/answer/<int:answer_id>')
@login_required
def review_answer(answer_id):
    check_res = check_answer(answer_id)
    if check_res is not None: return check_res

    answer = TestAnswer.query.filter_by(id=answer_id).first()

    if answer.reviewed:
        flash('Ta praca jest już oceniona', 'error')
        return redirect(url_for('manage'))

    return render_template('review.html', answer=answer, answer_nr=1, term_id=answer.term.id)


@app.route('/review/answer/<int:answer_id>', methods=['POST'])
@login_required
def review_post(answer_id):
    check_res = check_answer(answer_id)
    if check_res is not None: return check_res

    answer = TestAnswer.query.filter_by(id=answer_id).first()

    form = request.form
    valid = True
    points = {}

    # Validate
    try:
        for field in form.keys():
            question_nr = int(field)
            max_points = answer.get_answer_by_nr(question_nr).question.points
            provided_points = float(form[field])
            points[question_nr] = provided_points
            if not 0 <= provided_points <= max_points:
                valid = False
                break
    except ValueError:
        valid = False

    if not valid:
        flash('Niepoprawne dane', 'error')
        return redirect(url_for('review_answer', answer_id=answer_id, back=request.args.get('back', default=0)))

    # Update DB
    for question_nr in points.keys():
        question_answer = answer.get_answer_by_nr(question_nr)
        question_answer.given_points = points[question_nr]
        question_answer.reviewed = True
    db.session.commit()

    send_email(answer.email, 'Wyniki', 'test_result', answer=answer)

    flash('Praca została oceniona', 'success')

    back = request.args.get('back', default=0)
    if back == '1':
        return redirect(url_for('answers', term_id=answer.term.id))
    elif back == '2':
        return redirect(url_for('answer', answer_id=answer_id))
    else:
        return redirect(url_for('review_term', term_id=answer.term.id))
