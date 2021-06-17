from flask import render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app import app
from app.models import *
from app.util import *
from app.forms import AddTermForm
from app.email import send_email

def reset_edited():
    if session.get('editing_id') is not None:
        del session['editing_id']

@app.route('/manage')
@login_required
def manage():
    reset_edited()
    teacher = current_user
    tests = teacher.tests
    return render_template('manage.html', tests=tests)


@app.route('/details/<int:test_id>')
@login_required
def details(test_id):
    check_res = check_test(test_id)
    if check_res is not None: return check_res

    test = Test.query.filter_by(id=test_id).first()
    return render_template('details.html', test=test)


@app.route('/preview/<int:test_id>')
@login_required
def test_preview(test_id):
    check_res = check_test(test_id)
    if check_res is not None: return check_res

    test = Test.query.filter_by(id=test_id).first()
    return render_template('preview.html', test=test)


@app.route('/delete_test/<int:test_id>')
@login_required
def delete_test(test_id):
    check_res = check_test(test_id)
    if check_res is not None: return check_res

    test = Test.query.filter_by(id=test_id).first()
    db.session.delete(test)
    db.session.commit()

    flash('Pomyślnie usunięto test', 'success')
    return redirect(url_for('manage'))


@app.route('/add_term/<int:test_id>', methods=['GET', 'POST'])
@login_required
def add_term(test_id):
    check_res = check_test(test_id)
    if check_res is not None: return check_res

    form = AddTermForm()

    if form.validate_on_submit():
        test = Test.query.filter_by(id=test_id).first()
        term = TestTerm(name=form.name.data)
        test.terms.append(term)
        db.session.add(term)
        db.session.commit()

        flash('Pomyślnie dodano termin', 'success')
        return redirect(url_for('details', test_id=test_id))

    return render_template('add_term.html', form=form)


@app.route('/delete_term/<int:term_id>')
@login_required
def delete_term(term_id):
    check_res = check_term(term_id)
    if check_res is not None: return check_res

    term = TestTerm.query.filter_by(id=term_id).first()
    db.session.delete(term)
    db.session.commit()

    flash('Pomyślnie usunięto termin', 'success')
    return redirect(url_for('details', test_id=term.testid))


@app.route('/activate_term/<int:term_id>')
@login_required
def activate_term(term_id):
    check_res = check_term(term_id)
    if check_res is not None: return check_res

    term = TestTerm.query.filter_by(id=term_id).first()

    if term.status != TestTerm.PENDING:
        flash('Terminu nie można aktywować', 'error')
        return redirect(url_for('details', test_id=term.testid))

    term.status = TestTerm.ACTIVE
    db.session.commit()

    flash('Pomyślnie aktywowano termin', 'success')
    return redirect(url_for('details', test_id=term.testid))


@app.route('/finish_term/<int:term_id>')
@login_required
def finish_term(term_id):
    check_res = check_term(term_id)
    if check_res is not None: return check_res

    term = TestTerm.query.filter_by(id=term_id).first()

    if term.status != TestTerm.ACTIVE:
        flash('Terminu nie można zakończyć', 'error')
        return redirect(url_for('details', test_id=term.testid))

    term.auto_review_closed_questions()
    term.status = TestTerm.FINISHED
    db.session.commit()

    for answer in term.reviewed_answers:
        send_email(answer.email, 'Wyniki', 'test_result', answer=answer)

    flash('Pomyślnie zakończono termin', 'success')
    return redirect(url_for('details', test_id=term.testid))


@app.route('/export/<int:test_id>')
@login_required
def export_test(test_id):
    check_res = check_test(test_id)
    if check_res is not None: return check_res

    # TODO: Implement exporting test

    flash('Pomyślnie wyeksportowano test', 'success')
    return redirect(url_for('details', test_id=test_id))


@app.route('/import')
@login_required
def import_test():

    # TODO: Implement importing test

    flash('Pomyślnie zaimportowano test', 'success')
    return redirect(url_for('manage'))


@app.route('/answers/<int:term_id>')
@login_required
def answers(term_id):
    check_res = check_term(term_id=term_id)
    if check_res is not None: return check_res

    term = TestTerm.query.filter_by(id=term_id).first()
    return render_template('answers.html', term=term)


@app.route('/remove_answer/<int:answer_id>')
@login_required
def remove_answer(answer_id):
    check_res = check_answer(answer_id)
    if check_res is not None: return check_res

    answer = TestAnswer.query.filter_by(id=answer_id).first()
    term_id = answer.term.id
    db.session.delete(answer)
    db.session.commit()

    flash('Pomyślnie usunięto odpowiedź ucznia ' + answer.full_name, 'success')
    return redirect(url_for('answers', term_id=term_id))


@app.route('/answer/<int:answer_id>')
@login_required
def answer(answer_id):
    check_res = check_answer(answer_id)
    if check_res is not None: return check_res

    answer = TestAnswer.query.filter_by(id=answer_id).first()
    return render_template('answer.html', answer=answer)


