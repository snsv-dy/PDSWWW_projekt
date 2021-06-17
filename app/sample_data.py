import random

from app.models import *
import datetime


def initialize():

    if Teacher.query.first() is not None:
        return

    print('Initializing DB')

    teacher = Teacher(email='teacher@p.lodz.pl', full_name='Piotr Nowak')
    teacher.password = 'password'
    db.session.add(teacher)

    # for i in range(5):
    for i in range(1):
        add_test(teacher)

    # DELETE BEFORE PUSH
    #
    empty_test = Test(title='Empty for testing', time=25)
    teacher.tests.append(empty_test)
    db.session.add(empty_test)
    #
    #

    db.session.commit()


def add_test(teacher):
    test = Test(title='Test z przyrody', time=25)
    teacher.tests.append(test)
    db.session.add(test)

    q1 = Question(nr=1, question='Z jakich części składa się cep?', points=4, image=['baked_salmon.webp', 'jupiter.jpg'], type=Question.MULTIPLE_CHOICE, data={'all': ['Długi kij', 'Krótki kijek', 'Kawałek sznurka', 'Skrzynia biegów', 'Sprężarka', 'Spust', 'hehe'], 'correct': [0, 1, 2]})
    test.questions.append(q1)
    db.session.add(q1)

    q2 = Question(nr=2, question='Co jest cięższe?', points=4, image=None, type=Question.SINGLE_CHOICE, data={'all': ['1kg piór', '1kg stali'], 'correct': 1})
    test.questions.append(q2)
    db.session.add(q2)

    q3 = Question(nr=3, question='To po prawo to tak naprawdę nie jest zdjęcie jowisza, tylko staw z kaczkami', points=6, image=['jupiter.jpg'], type=Question.OPEN)
    test.questions.append(q3)
    db.session.add(q3)

    for i in range(1):
        add_term(test)


def add_term(test):
    term = TestTerm(name="Termin pierwszy")
    test.terms.append(term)
    db.session.add(term)

    for i in range(10):
        add_answers(term)


def add_answers(term):
    test_answer = TestAnswer(email='student@edu.p.lodz.pl', full_name='Mateusz Kowalski')
    term.answers.append(test_answer)
    db.session.add(test_answer)

    a1 = QuestionAnswer(data=[0, 1])
    q = term.test.questions[0]
    q.answers.append(a1)
    test_answer.answers.append(a1)
    db.session.add(a1)

    a2 = QuestionAnswer(data=1)
    q = term.test.questions[1]
    q.answers.append(a2)
    test_answer.answers.append(a2)
    db.session.add(a2)

    a3 = QuestionAnswer(data='Nie wiem')
    q = term.test.questions[2]
    q.answers.append(a3)
    test_answer.answers.append(a3)
    db.session.add(a3)
