from app.emails import send_email
from flask import render_template, current_app
from datetime import datetime


def send_error_email(user, trigger):
    send_email('ERROR 500 REPORTED!',
               sender=current_app.config['ADMINS'][0],
               recipients=['gilad@ilmjtcv.com'],
               text_body=render_template('errors/email/500_found.txt', user=user, trigger=trigger,
                                         date=str(datetime.utcnow())),
               html_body=render_template('errors/email/500_found.html', user=user, trigger=trigger,
                                         date=str(datetime.utcnow())))