from flask import flash, render_template, request, url_for, redirect
from flask_login import login_user, logout_user
from app.forms import LoginForm, RegistrationForm
from app.models import *
from app import app
from app.util import display_form_errors


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        teacher = Teacher.query.filter_by(email=form.email.data.lower()).first()
        if teacher is None:
            flash('Podany email nie jest zarejestrowany', 'error')
            return render_template('login.html', form=form)
        if teacher.verify_password(form.password.data):
            login_user(teacher, remember=form.remember_me.data)
            flash('Zalogowano pomyślnie!', 'success')

            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('manage')
            return redirect(next)

        flash('Niepoprawne hasło', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        teacher = Teacher(email=form.email.data.lower(), password=form.password.data)
        db.session.add(teacher)
        db.session.commit()
        flash('Zostałeś pomyślnie zarejestrowany!', 'success')
        return redirect(url_for('index'))
    display_form_errors(form)
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    flash('Zostałeś pomyślnie wylogowany', 'success')
    logout_user()
    return redirect(url_for('index'))