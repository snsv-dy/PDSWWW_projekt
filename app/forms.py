from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email


EMAIL_VALIDATOR = Email(message='Invalid email address')


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Hasło')
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')
