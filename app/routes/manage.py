import json
from json import JSONEncoder

import pdb
from flask import render_template, flash, redirect, url_for, session, make_response, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

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
    test = Test.query.filter_by(id=test_id).first()

    class ExportedQuestion:
        def __init__(self, number, question, type, answers, correct, points, images):
            self.number = number
            self.question = question
            self.type = type
            self.answers = answers
            self.correct = correct
            self.points = points
            self.images = images

    class ExportedTest:
        def __init__(self, title, questions, time):
            self.time = time
            self.title = title
            self.questions = questions

    exp_list = []
    for question in test.questions:
        if  question.type == Question.MULTIPLE_CHOICE:
            exp_quest = ExportedQuestion(question.nr, question.question, question.type, question.data['all'], question.data['correct'], question.points, question.image)
            exp_list.append(exp_quest)
        elif question.type == Question.SINGLE_CHOICE:
            exp_quest = ExportedQuestion(question.nr, question.question, question.type, question.data['all'], question.data['correct'], question.points, question.image)
            exp_list.append(exp_quest)
        elif question.type == Question.OPEN:
            exp_quest = ExportedQuestion(question.nr, question.question, question.type, [], [], question.points, question.image)
            exp_list.append(exp_quest)

    exp_test = ExportedTest(test.title, exp_list, test.time)
    file = json.dumps(exp_test, default=lambda o: o.__dict__, indent=4)

    response = make_response(file)
    response.headers.set('Content-Type', 'text/plain')
    response.headers.set('Content-Disposition', 'attachment', filename='%s.json'%test.title)
    return response



@app.route('/upload')
@login_required
def upload_test():
    return render_template('upload_file.html')


@app.route('/import', methods = ['GET', 'POST'])
@login_required
def import_test():
    def validate_json(data):
        # FIELD MISSING IN HEADER
        # LOOKS ATROCIOUS BUT all() with this datatype doesn't work
        if 'title' not in data or 'time' not in data or 'questions' not in data:
            return False, "fields missing in header"
        # NO TITLE
        if len(data['title']) < 1:
            return False, "title is empty"
        # TIME INCORRECT
        if data['time'] < 1 or data['time'] > 60:
            return False, "time is incorrect"
        # NO QUESTIONS
        if len(data['questions']) < 1:
            return False, "no questions found in file"
        # EACH QUESTION
        for question in data['questions']:
            # FIELD MISSING IN QUESTION
            # LOOKS ATROCIOUS BUT all() with this datatype doesn't work
            if 'question' not in question or 'points' not in question or 'images' not in question or 'type' not in question or 'answers' not in question or 'correct' not in question or 'type' not in question:
                return False, "fields missing in question"
            # QUESTION FIELDS EMPTY
            if len(question['question']) < 0:
                return False, "question title is empty"
            # CHECK FOR TYPE
            if question['type'] == Question.SINGLE_CHOICE or question['type'] == Question.MULTIPLE_CHOICE:
                # NO ANSWERS
                if len(question['answers']) < 1:
                    return False, "no answers found for question"
                # ANSWER FIELD EMPTY
                for answer in question['answers']:
                    if len(answer) < 1:
                        return False, "empty field in answers"
                # NO CORRECT ANSWERS (MULTIPLE CHECK ONLY)
                if question['type'] == Question.MULTIPLE_CHOICE:
                    if len(question['correct']) < 1:
                        return False, "no correct answers found"
                    # CORRECT ANSWER OUT OF RANGE
                    for correct in question['correct']:
                        if correct < 0 or correct > len(question['answers']):
                            return False, "correct answer out of range"
                # NO CORRECT ANSWERS (SINGLE CHOICE)
                if question['type'] == Question.SINGLE_CHOICE:
                    if question['correct'] < 0 or question['correct'] > len(question['answers']):
                        return False, "correct answer out of range"
                # CORRECT POINTS
                if question['points'] < 1:
                    return False, "incorrect value of points"
            # TYPE DOES NOT MATCH ANY
            elif question['type'] != Question.OPEN:
                return False, "incorrect question type"
        # VALIDATION CORRECT
        return True, "all good"
    teacher = current_user
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        if filename == '':
            flash('Nie wysłano żadnego pliku')
            return render_template('upload_file.html')

        json_data = json.load(f)
        check, err_msg = validate_json(json_data)
        if (check):
            test = Test(title=json_data['title'], time=json_data['time'])
            teacher.tests.append(test)
            db.session.add(test)
            for question in json_data['questions']:
                quest = Question(nr=question['number'], question=question['question'], points=question['points'], image=question['images'], type=question['type'], data={'all': question['answers'], 'correct': question['correct']})
                test.questions.append(quest)
                db.session.add(quest)
            db.session.commit()
        else:
            flash('Nadesłany plik jest uszkodzony! Opis błędu: ' + err_msg, 'error')
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


