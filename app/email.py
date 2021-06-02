from flask_mail import Message
from flask import render_template
from app import mail, app
from threading import Thread


SENDER = 'Szybki Test'
SUBJECT_PREFIX = 'Szybki Test - '


def send_email(to, subject, template, **kwargs):
    msg = Message(SUBJECT_PREFIX + subject, sender=SENDER, recipients=[to])
    msg.body = render_template('emails/' + template + '.txt', **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
