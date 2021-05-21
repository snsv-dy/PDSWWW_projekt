from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError

from app import db
from app.models import Teacher


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Hasło')
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class RegistrationForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Hasło')
    password_confirmation = PasswordField('Powtórzone hasło')
    submit = SubmitField('Zarejestruj')

    @staticmethod
    def validate_email(_, field):
        if Teacher.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered')
