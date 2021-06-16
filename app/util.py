from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import *


def display_form_errors(form):
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')


def check_test(test_id):
    test = Test.query.filter_by(id=test_id).first()

    if test is None:
        flash('Żądany test nie istnieje', 'error')
        return redirect(url_for('manage'))

    if test.teacherid != current_user.id:
        flash('Nie jesteś uprawiony do tego testu', 'error')
        return redirect(url_for('manage'))

    return None


def check_term(term_id):
    term = TestTerm.query.filter_by(id=term_id).first()

    if term is None:
        flash('Żądany termin nie istnieje', 'error')
        return redirect(url_for('manage'))

    if term.test.teacherid != current_user.id:
        flash('Nie jesteś uprawiony do tego terminu', 'error')
        return redirect(url_for('manage'))

    return None


def check_answer(answer_id):
    answer = TestAnswer.query.filter_by(id=answer_id).first()

    if answer is None:
        flash('Żądana odpowiedź nie istnieje', 'error')
        return redirect(url_for('manage'))

    if answer.term.test.teacherid != current_user.id:
        flash('Nie jesteś uprawiony do oglądania tej odpowiedzi', 'error')
        return redirect(url_for('manage'))

    return None
