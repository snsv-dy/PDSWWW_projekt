from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from datetime import datetime
from random import randint


class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String)
    tests = db.relationship("Test", backref="teacher", lazy='select')

    @property
    def password(self):
        raise AttributeError('Password is read only')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Question(db.Model):

    MULTIPLE_CHOICE = 0
    SINGLE_CHOICE = 1
    OPEN = 2

    id = db.Column(db.Integer, primary_key=True)
    nr = db.Column(db.Integer)  # Nr pytania: 1, 2, 3 itd
    question = db.Column(db.String)
    points = db.Column(db.Float)
    image = db.Column(db.PickleType)
    testid = db.Column(db.Integer, db.ForeignKey('test.id'))
    type = db.Column(db.Integer)
    data = db.Column(db.PickleType)
    answers = db.relationship("QuestionAnswer", backref="question", lazy='select')


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.relationship("Question", backref="test", lazy='select', order_by='Question.nr', cascade='all,delete')
    title = db.Column(db.String, default="Brak nazwy")
    time = db.Column(db.Integer, default=10)    # In minutes
    teacherid = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    terms = db.relationship("TestTerm", backref="test", lazy='select', cascade='all,delete')

    def get_questions_count(self):
        single_choice_count = 0
        multiple_choice_count = 0
        open_count = 0

        for question in self.questions:
            if question.type == Question.SINGLE_CHOICE:
                single_choice_count += 1
            elif question.type == Question.MULTIPLE_CHOICE:
                multiple_choice_count += 1
            elif question.type == Question.OPEN:
                open_count += 1

        return single_choice_count, multiple_choice_count, open_count

    def get_pending_terms(self):
        return [term for term in self.terms if term.status == TestTerm.PENDING]

    def get_active_terms(self):
        return [term for term in self.terms if term.status == TestTerm.ACTIVE]

    def get_finished_terms(self):
        return [term for term in self.terms if term.status == TestTerm.FINISHED]

    def get_question_by_nr(self, nr):
        return [question for question in self.questions if question.nr == nr][0]


def random_term_code():
    while True:
        code = randint(100000, 999999)
        busy = TestTerm.query.filter_by(code=code).first()
        if not busy:
            return code


class TestTerm(db.Model):
    PENDING = 0
    ACTIVE = 1
    FINISHED = 2

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, default=random_term_code)
    status = db.Column(db.Integer, default=PENDING)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String, default='Brak nazwy')
    testid = db.Column(db.Integer, db.ForeignKey('test.id'))
    answers = db.relationship("TestAnswer", backref="term", lazy='select', cascade='all,delete')

    @property
    def reviewed_answers(self):
        return [answer for answer in self.answers if answer.reviewed]

    @property
    def not_reviewed_answers(self):
        return [answer for answer in self.answers if not answer.reviewed]

    def auto_review_closed_questions(self):
        for answer in self.answers:
            answer.auto_review_closed_questions()


class TestAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    full_name = db.Column(db.String)
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)
    test_term_id = db.Column(db.Integer, db.ForeignKey('test_term.id'))
    answers = db.relationship("QuestionAnswer", backref="test_answer", lazy='select', cascade='all,delete')

    @property
    def given_points(self):
        return sum([answer.given_points for answer in self.answers])

    @property
    def max_points(self):
        return sum([question.points for question in self.term.test.questions])

    @property
    def reviewed(self):
        # TestAnswer is reviewed if all QuestionAnswer are reviewed
        return all([answer.reviewed for answer in self.answers])

    @property
    def open_answers(self):
        return [answer for answer in self.answers if answer.question.type == Question.OPEN]

    @property
    def grade(self):
        if self.max_points == 0:
            return 5
        percent = self.given_points / self.max_points * 100
        if percent >= 90: return 5
        elif percent >= 75: return 4
        elif percent >= 50: return 3
        else: return 2

    def get_answer_by_nr(self, nr):
        return [answer for answer in self.answers if answer.question.nr == nr][0]

    def auto_review_closed_questions(self):
        for answer in self.answers:
            answer.auto_review()


class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.PickleType)
    reviewed = db.Column(db.Boolean, default=False)
    given_points = db.Column(db.Float, default=0)
    test_answer_id = db.Column(db.Integer, db.ForeignKey('test_answer.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def auto_review(self):
        if self.question.type != Question.OPEN:
            self.given_points = self.calc_points()
            self.reviewed = True
            db.session.add(self)
            db.session.commit()

    def calc_points(self):
        if self.data is None:
            return 0

        if self.question.type == Question.SINGLE_CHOICE:
            correct = self.question.data['correct']
            if False:
                print('******* no correct single')
                return 0
            provided = self.data
            print('************** validating single choice: ', correct, provided)
            return self.question.points if provided == correct else 0
    
        elif self.question.type == Question.MULTIPLE_CHOICE:
            correct = self.question.data['correct']
            if not correct:
                print('******* no correct multiple')
                return 0
            provided = self.data
    
            points_per_option = self.question.points / len(correct)
            points = 0
            print('******** validating multiple choice: ', correct, provided)
            for option in provided:
                if option in correct:
                    points += points_per_option
                else:
                    points -= points_per_option
    
            points = max(points, 0)
            points = round(points * 2) / 2
            return points
    
        else:
            return 0
