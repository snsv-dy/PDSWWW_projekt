from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from app.models import Teacher

EMAIL_VALIDATOR = Email(message='Nieprawidłowy format adresu email')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), EMAIL_VALIDATOR])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), EMAIL_VALIDATOR])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=8, message='Długość hasła musi wynosić co najmniej 8 znaków')])
    password_confirmation = PasswordField('Powtórzone hasło', validators=[DataRequired(), EqualTo('password', message='Hasła nie są identyczne')])
    submit = SubmitField('Zarejestruj')

    @staticmethod
    def validate_email(_, field):
        if Teacher.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Podany adres email jest już zarejestrowany')


class BeforeTestForm(FlaskForm):
    name = StringField('Twoje imie i nazwisko', validators=[DataRequired()])
    email = StringField('Twój adres e-mail', validators=[DataRequired(), EMAIL_VALIDATOR])
    submit = SubmitField('Rozpocznij test')
