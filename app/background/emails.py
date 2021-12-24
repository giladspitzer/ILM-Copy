from app.emails import send_email, add_activity
from flask import render_template, current_app

def send_email_partnership_approved(recruiter):
    token = recruiter.get_initial_confirm_token()
    send_email('Partnership Approved!',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('background/email/partnership_approved.txt',
                                         recruiter=recruiter, token=token),
               html_body=render_template('background/email/partnership_approved.html',
                                         recruiter=recruiter, token=token))
    add_activity(recruiter.user, 10)


def send_email_partnership_rejected(recruiter):
    token = recruiter.get_initial_confirm_token()
    send_email('Partnership Status Update',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('background/email/partnership_rejected.txt',
                                         recruiter=recruiter, token=token),
               html_body=render_template('background/email/partnership_rejected.html',
                                         recruiter=recruiter, token=token))
    add_activity(recruiter.user, 28)


def send_email_partnership_approved_try_again(recruiter):
    token = recruiter.get_initial_confirm_token()
    send_email('REMINDER: Partnership Approved!',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('background/email/partnership_approved_try_again.txt',
                                         recruiter=recruiter, token=token),
               html_body=render_template('background/email/partnership_approved_try_again.html',
                                         recruiter=recruiter, token=token))
    add_activity(recruiter.user, 25)



def send_email_map_update(users):
    send_email('Map Updated!',
               sender=current_app.config['ADMINS'][0],
               recipients=['dev@ilmjtcv.com'],
               text_body=render_template('background/email/map_updater.txt',
                                         user=users),
               html_body=render_template('background/email/map_updater.html',
                                         users=users))


def send_email_new_jobs(user):
    add_activity(user, 6)
    if not user.unsubscribed:
        send_email('We found new job listings for you!',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('background/email/new_jobs.txt',
                                             user=user),
                   html_body=render_template('background/email/new_jobs.html',
                                             user=user))


def send_email_jobs_updated(total, successful, entire=0):
    send_email('Jobs have been updated!',
               sender=current_app.config['ADMINS'][0],
               recipients=['dev@ilmjtcv.com'],
               text_body=render_template('background/email/jobs_update.txt',
                                         user=total, successful=successful),
               html_body=render_template('background/email/jobs_update.html',
                                         users=total, successful=successful))


def send_email_new_candidates_found(search):
    send_email('Candidates have been found for your search!',
               sender=current_app.config['ADMINS'][0],
               recipients=[x.recruiter.user.email for x in search.recruiters],
               text_body=render_template('background/email/candidates_found.txt',
                                         search=search),
               html_body=render_template('background/email/candidates_found.html',
                                         search=search))
    for x in search.recruiters:
        add_activity(x.recruiter.user, 27)



# def send_email_no_activity(user, stats):
#     if not user.unsubscribed:
#         send_email('We miss you!',
#                    sender=current_app.config['ADMINS'][0],
#                    recipients=[user.email],
#                    text_body=render_template('background/email/no_activity.txt',
#                                              stats=stats, user=user),
#                    html_body=render_template('background/email/no_activity.html',
#                                              stats=stats, user=user))
#         add_activity(user, 12)
#
#
# def send_email_never_finished(user, time_left):
#
#     token = user.get_email_confirmation_token()
#     send_email('Complete Your Registration!',
#                sender=current_app.config['ADMINS'][0],
#                recipients=[user.email],
#                text_body=render_template('background/email/never_finished.txt',
#                                          time_left=time_left, user=user, token=token),
#                html_body=render_template('background/email/never_finished.html',
#                                          time_left=time_left, user=user, token=token))
#     add_activity(user, 13)
#
#
# def send_email_user_deleted(user):
#     send_email('User Deleted',
#                sender=current_app.config['ADMINS'][0],
#                recipients=['gilad@ilmjtcv.com'],
#                text_body=render_template('background/email/user_deleted.txt',
#                                          user=user),
#                html_body=render_template('background/email/user_deleted.html',
#                                          user=user))


def send_email_never_enrolled_recruiting(user):
    if not user.unsubscribed:
        send_email('Recruiter Visibility!',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('background/email/never_enrolled_recruiting.txt',
                                             user=user),
                   html_body=render_template('background/email/never_enrolled_recruiting.html',
                                             user=user))
        add_activity(user, 26)


def send_email_custom_message(user, email):
    if not user.unsubscribed:
        send_email(email.subject,
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('background/email/custom/custom_message.txt',
                                             user=user, email=email),
                   html_body=render_template('background/email/custom/custom_message.html',
                                             user=user, email=email))
        add_activity(user, 50)


def send_email_custom_sending_done(user, num, email):
    send_email('Mass Email Sending Done',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/custom/sending_done.txt',
                                         num=num, user=user, email=email),
               html_body=render_template('background/email/custom/sending_done.html',
                                         num=num, user=user, email=email))


def send_email_custom_message_test(user, num, email):
    token = email.get_sending_confirmation_token()
    send_email(email.subject,
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/custom/custom_message_testing.txt',
                                         num=num, user=user, email=email, token=token),
               html_body=render_template('background/email/custom/custom_message_testing.html',
                                         num=num, user=user, email=email, token=token))

def send_email_to_devs(text):
    send_email('Custom Message for Devs',
               sender=current_app.config['ADMINS'][0],
               recipients=['gilad@ilmjtcv.com'],
               text_body=render_template('background/email/special_message.txt',
                                         text=text),
                html_body = render_template('background/email/special_message.txt',
                                text=text)
    )

def send_email_appointment_join_mentee(user, appointment):
    send_email('Your Mentorship Appointment Is Starting in 5 Minutes!!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/sessions/mentee_starting.txt',
                                         user=user, appointment=appointment),
               html_body=render_template('background/email/sessions/mentee_starting.html',
                                         user=user, appointment=appointment))
    add_activity(user, 216)

def send_email_appointment_join_mentor(user, appointment):
    send_email('Your Mentorship Appointment Is Starting in 5 Minutes!!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/sessions/mentor_starting.txt',
                                         user=user, appointment=appointment),
               html_body=render_template('background/email/sessions/mentor_starting.html',
                                         user=user, appointment=appointment))
    add_activity(user, 215)

def send_email_appointment_follow_up(user, appointment):
    send_email('How Did Your Mentorship Session Go?',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/sessions/follow_up.txt',
                                         user=user, appointment=appointment),
               html_body=render_template('background/email/sessions/follow_up.html',
                                         user=user, appointment=appointment))
    add_activity(user, 217)


def send_email_event_reminder(user, event):
    send_email('Exclusive Event Starting Soon!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/event_reminder.txt',
                                         user=user, event=event),
               html_body=render_template('background/email/event_reminder.html',
                                         user=user, event=event))
    add_activity(user, 218)


def send_email_recruiter_inactive(user):
    send_email('Updates to your Recruiter Portal',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/recruiter_inactive.txt',
                                         user=user),
               html_body=render_template('background/email/recruiter_inactive.html',
                                         user=user))
    add_activity(user, 500)


def send_email_mentor_inactive(user):
    send_email('Give Back to the Unemployed Community',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/mentor_inactive.txt',
                                         user=user),
               html_body=render_template('background/email/mentor_inactive.html',
                                         user=user))
    add_activity(user, 502)


def send_email_mentor_incomplete(user):
    send_email('Complete Your Mentorship Registration',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/mentor_incomplete.txt',
                                         user=user),
               html_body=render_template('background/email/mentor_incomplete.html',
                                         user=user))
    add_activity(user, 503)

def send_email_user_roundup(user):
    send_email('Your ILMJTCV Digest',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/user_digest.txt',
                                         user=user),
               html_body=render_template('background/email/user_digest.html',
                                         user=user))
    add_activity(user, 501)

def send_email_event_reminder_special(user, event):
    send_email('Webinar starting in 5 minutes!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('background/email/event_reminder_all.txt',
                                         user=user, event=event),
               html_body=render_template('background/email/event_reminder_all.html',
                                         user=user, event=event))
    add_activity(user, 218)