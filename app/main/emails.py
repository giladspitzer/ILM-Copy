from app.emails import send_email, add_activity, send_special_email
from flask import render_template, current_app


def send_error_email(form):
    send_email('[INTERNAL-ILMJTCV] Error Submitted!',
               sender=current_app.config['ADMINS'][0],
               recipients=['sigal@ilmjtcv.com', 'gilad@ilmjtcv.com', 'zach@ilmjtcv.com'],
               text_body=render_template('main/email/error_reported.txt', form=form),
               html_body=render_template('main/email/error_reported.html', form=form))


def send_user_confirmed_report(user, description):
    if not user.unsubscribed:
        send_email('Post Reported!',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/_user_post_reported.txt', description=description, user=user),
                   html_body=render_template('main/email/_user_post_reported.html', description=description, user=user))
        add_activity(user, 7)


def send_dev_confirmed_report(user, description):
    send_email('Post Reported!',
               sender=current_app.config['ADMINS'][0],
               recipients=['nickfields67@gmail.com', 'gilad@ilmjtcv.com', 'sigal@ilmjtcv.com'],
               text_body=render_template('main/email/_dev_post_reported.txt', user=user, description=description),
               html_body=render_template('main/email/_dev_post_reported.html', user=user, description=description
                                         ))

def send_email_recruiting_enroll(user):
    if not user.unsubscribed:
        send_email('Welcome to ILMJTCV-Jobs',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/recruiting_enroll.txt', user=user),
                   html_body=render_template('main/email/recruiting_enroll.html', user=user))
        add_activity(user, 8)


def send_email_recruiting_unenroll(user):
    if not user.unsubscribed:
        send_email('Un-enrolled From Recruiter Resume Access',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/recruiting_unenroll.txt', user=user),
                   html_body=render_template('main/email/recruiting_unenroll.html',user=user))
        add_activity(user, 9)



def send_email_new_testimonial(testimonial):
    send_email('New Testimonial',
               sender=current_app.config['ADMINS'][0],
               recipients=['gilad@ilmjtcv.com', 'sigal@ilmjtcv.com', 'zach@ilmjtcv.com'],
               text_body=render_template('main/email/new_testimonial.txt', t=testimonial),
               html_body=render_template('main/email/new_testimonial.html', t=testimonial))

def send_email_confirm_unapply(job, user):
    if not user.unsubscribed:
        send_email('Job Application Withdrawn',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/confirm_unapply.txt', user=user, job=job),
                   html_body=render_template('main/email/confirm_unapply.html', user=user, job=job))
        add_activity(user, 12)

def send_email_confirm_apply(job, user):
    if not user.unsubscribed:
        send_email('Job Application Submitted!',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/confirm_apply.txt', user=user, job=job),
                   html_body=render_template('main/email/confirm_apply.html', user=user, job=job))
        add_activity(user, 11)


def send_email_job_no_longer_available(job, user):
    if not user.unsubscribed:
        send_email('Job No Longer Available',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/job_no_longer_available.txt', user=user, job=job),
                   html_body=render_template('main/email/job_no_longer_available.html', user=user, job=job))

def send_email_job_available_again(job, user):
    if not user.unsubscribed:
        send_email('Job Posting Available Again!',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('main/email/job_available_again.txt', user=user, job=job),
                   html_body=render_template('main/email/job_available_again.html', user=user, job=job))

def send_email_event_rsvp(user, event):
    send_special_email('Event RSVP Received!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               attachments=[event.get_attachment()],
               text_body=render_template('main/email/events/rsvp_event.txt', user=user, event=event),
               html_body=render_template('main/email/events/rsvp_event.html', user=user, event=event))
    add_activity(user, 13)

def send_email_event_unrsvp(user, event):
    send_email('Can No Longer Attend?',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('main/email/events/unrsvp_event.txt', user=user, event=event),
               html_body=render_template('main/email/events/unrsvp_event.html', user=user, event=event))
    add_activity(user, 14)

def send_email_mentor_info_update(user):
    send_email('Your Mentor Profile Has Been Updated',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('main/email/mentor/mentor_profile_update.txt', user=user),
               html_body=render_template('main/email/mentor/mentor_profile_update.html', user=user))
    add_activity(user, 150)


def send_email_appointment_confirmed(user, appointment):
    send_special_email('Mentorship Appointment Confirmation',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               attachments=[appointment.get_attachment()],
               text_body=render_template('main/email/mentor/mentor_appointment_confirm.txt', user=user, appointment=appointment),
               html_body=render_template('main/email/mentor/mentor_appointment_confirm.html', user=user, appointment=appointment))
    add_activity(user, 160)


def send_email_appointment_cancelled_mentor(user, appointment, person):
    send_special_email('IMPORTANT: Mentorship Appointment Cancelled',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               attachments=[appointment.get_cancelled_attachment()],
               text_body=render_template('main/email/mentor/mentor_appointment_canclled.txt', user=user, appointment=appointment, self=person),
               html_body=render_template('main/email/mentor/mentor_appointment_canclled.html', user=user, appointment=appointment, self=person))
    add_activity(user, 180)

def send_email_appointment_cancelled_mentee(user, appointment, person):
    send_special_email('IMPORTANT: Mentorship Appointment Cancelled',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               attachments=[appointment.get_cancelled_attachment()],
               text_body=render_template('main/email/mentor/mentee_appointment_canclled.txt', user=user, appointment=appointment, self=person),
               html_body=render_template('main/email/mentor/mentee_appointment_canclled.html', user=user, appointment=appointment, self=person))
    add_activity(user, 190)


def send_email_appointment_filled(user, appointment):
    send_special_email('Somebody Has Signed Up For Your Mentorship Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               attachments=[appointment.get_attachment()],
               text_body=render_template('main/email/mentor/mentor_appointment_filled.txt', user=user, appointment=appointment),
               html_body=render_template('main/email/mentor/mentor_appointment_filled.html', user=user, appointment=appointment))
    add_activity(user, 170)

def send_email_mentor_approved(user):
    send_email('Your Mentorship Application Has Been Approved!',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('main/email/mentor/mentor_approved.txt', user=user),
               html_body=render_template('main/email/mentor/mentor_approved.html', user=user))
    add_activity(user, 200)

def send_email_mentor_app_receivied(user):
    send_email('We Have Received Your Application',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('main/email/mentor/mentor_received.txt', user=user),
               html_body=render_template('main/email/mentor/mentor_received.html', user=user))
    add_activity(user, 210)

def send_email_mentor_rejected(user):
    send_email('Mentorship Application Update',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('main/email/mentor/mentor_rejected.txt', user=user),
               html_body=render_template('main/email/mentor/mentor_rejected.html', user=user))
    add_activity(user, 220)