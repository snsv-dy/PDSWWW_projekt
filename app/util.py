from flask import flash


def display_form_errors(form):
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')