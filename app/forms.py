from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Hasło')
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')
