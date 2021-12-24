from app.emails import send_email, add_activity
from flask import render_template, current_app


def send_email_devs_new_partnership(org):
    send_email('NEW PARTNERSHIP REQUEST!',
               sender=current_app.config['ADMINS'][0],
               recipients=['gilad@ilmjtcv.com', 'sigal@ilmjtcv.com', 'zach@ilmjtcv.com'],
               text_body=render_template('auth/email/new_partnership_request.txt',
                                         org=org),
               html_body=render_template('auth/email/new_partnership_request.html',
                                         org=org))

def send_email_partnership_received(org):
    send_email('Partnership Request Received!',
               sender=current_app.config['ADMINS'][0],
               recipients=[org.request_email],
               text_body=render_template('auth/email/partnership_confirmed.txt',
                                         user=org.request_name),
               html_body=render_template('auth/email/partnership_confirmed.html',
                                         user=org.request_name))


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/reset_password_email.html',
                                         user=user, token=token))
    add_activity(user, 2)


def send_email_confirm_email(user):
    token = user.get_email_confirmation_token()
    send_email('Confirm Your Account',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/confirm_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/confirm_email.html',
                                         user=user, token=token))
    add_activity(user, 0)


def send_email_confirm_email_mentor(user):
    token = user.get_email_confirmation_token()
    send_email('One Last Step...',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/confirm_email_mentor.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/confirm_email_mentor.html',
                                         user=user, token=token))
    add_activity(user, 0)


def send_email_confirm_registration(user):
    send_email('Account Registration Confirmed',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/account_registration_confirmed.txt',
                                         user=user),
               html_body=render_template('auth/email/account_registration_confirmed.html',
                                         user=user))
    add_activity(user, 1)


def send_email_confirm_password_reset(user):
    send_email('Your Password Has Been Reset',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/password_reset_confirmed.txt',
                                         user=user),
               html_body=render_template('auth/email/password_reset_confirmed.html',
                                         user=user))
    add_activity(user, 3)


def send_email_confirm_new_email(user):
    token = user.get_email_confirmation_token()
    send_email('Your Email Has Been Reset',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/confirm_new_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/confirm_new_email.html',
                                         user=user, token=token))
    add_activity(user, 4)


def send_email_edit_profile_changes(user, changes):
    send_email('Your profile has been updated',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/confirm_account_changes.txt',
                                         user=user, changes=changes),
               html_body=render_template('auth/email/confirm_account_changes.html',
                                         user=user, changes=changes))
    add_activity(user, 5)

def send_email_account_deletion_request(user):
    token = user.get_account_deletion_token()
    print(token)
    send_email('Account Deletion Request',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/delete_account_request.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/delete_account_request.html',
                                         user=user, token=token))
    add_activity(user, 100)


def send_email_account_deletion_confirmed(user):
    send_email('Your Account Has Been Deleted :(',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/delete_account_confirm.txt',
                                         name=user.name),
               html_body=render_template('auth/email/delete_account_confirm.html',
                                        name=user.name))
    add_activity(user, 99)


def send_email_confirm_recruiter_registration(user):
    send_email('Recruiter Registration Completed',
               sender='sigal@ilmjtcv.com',
               recipients=[user.email],
               text_body=render_template('auth/email/confirm_recruiter_registration.txt',
                                         name=user.name),
               html_body=render_template('auth/email/confirm_recruiter_registration.html',
                                         name=user.name))
    add_activity(user, 100)