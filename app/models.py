from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


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

    SINGLE_CHOICE = 0
    MULTIPLE_CHOICE = 1
    OPEN = 2

    id = db.Column(db.Integer, primary_key=True)
    nr = db.Column(db.Integer)
    question = db.Column(db.String)
    points = db.Column(db.Float)
    image = db.Column(db.PickleType)
    testid = db.Column(db.Integer, db.ForeignKey('test.id'))
    type = db.Column(db.Integer)
    data = db.Column(db.PickleType)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.relationship("Question", backref="test", lazy='select')
    title = db.Column(db.String)
    teacherid = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    terms = db.relationship("TestTerm", backref="test", lazy='select')


class TestTerm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    code = db.Column(db.Integer)
    testid = db.Column(db.Integer, db.ForeignKey('test.id'))
    answers = db.relationship("TestAnswer", backref="test_term", lazy='select')


class TestAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    full_name = db.Column(db.String)
    test_term_id = db.Column(db.Integer, db.ForeignKey('test_term.id'))
    answers = db.Column(db.PickleType)
