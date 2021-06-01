from app.models import *
import datetime


def initialize():

    if Teacher.query.first() is not None:
        return

    print('Initializing DB')

    teacher = Teacher(email='teacher@p.lodz.pl', full_name='Piotr Nowak')
    teacher.password = 'password'
    db.session.add(teacher)

    test = Test(title='Test z przyrody')
    teacher.tests.append(test)
    db.session.add(test)

    question1 = Question(question='Z jakich części składa się cep?', points=4, image=None, type=Question.MULTIPLE_CHOICE, data={'all': ['Długi kij', 'Krótki kijek' 'Kawałek sznurka', 'Skrzynia biegów', 'Sprężarka', 'Spust', 'hehe'], 'correct': [0, 1, 2]})
    test.questions.append(question1)
    db.session.add(question1)

    question2 = Question(question='Co jest cięższe?', points=4, image=None, type=Question.SINGLE_CHOICE, data={'all': ['1kg piór', '1kg stali'], 'correct': 0})
    test.questions.append(question2)
    db.session.add(question2)

    question3 = Question(question='To po prawo to tak naprawdę nie jest zdjęcie jowisza, tylko staw z kaczkami', points=6, image=None, type=Question.OPEN)
    test.questions.append(question3)
    db.session.add(question3)

    term = TestTerm(time=datetime.datetime.now(), code=123)
    test.terms.append(term)
    db.session.add(term)

    answer = TestAnswer(email='student@edu.p.lodz.pl', full_name='Mateusz Kowalski', answers=[1])
    term.answers.append(answer)
    db.session.add(answer)

    db.session.commit()
