from app.emails import send_email, add_activity
from flask import render_template, current_app



def send_email_confirm_recruiter(recruiter):
    token = recruiter.get_initial_confirm_token()
    send_email('Recruiter Account Created',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/new_recruiter.txt',
                                         recruiter=recruiter, token=token),
               html_body=render_template('partnership/email/new_recruiter.html',
                                         recruiter=recruiter, token=token))

    add_activity(recruiter.user, 24)


def send_email_new_recruiter_admin(admins, recruiter):
    send_email('Recruiter Added',
               sender=current_app.config['ADMINS'][0],
               recipients=admins,
               text_body=render_template('partnership/email/new_recruiter_confirmed.txt',
                                         recruiter=recruiter),
               html_body=render_template('partnership/email/new_recruiter_confirmed.html',
                                         recruiter=recruiter))



def send_email_new_job_posting_quick(recruiter, job):
    send_email('Job Added! (' + str(job.job_title) + ' -- ILMJTCV Quick Apply)',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/new_job_posted_quick.txt',
                                         recruiter=recruiter, job=job),
               html_body=render_template('partnership/email/new_job_posted_quick.html',
                                         recruiter=recruiter, job=job))
    add_activity(recruiter.user, 23)


def send_email_new_job_posting(recruiter, job):
    send_email('External Job Added! (' + str(job.job_title) + ')',
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/new_job_posted.txt',
                                         recruiter=recruiter, job=job),
               html_body=render_template('partnership/email/new_job_posted.html',
                                         recruiter=recruiter, job=job))

    add_activity(recruiter.user, 22)



def send_email_job_deleted(recruiter, job):
    send_email('Job Posting Deleted: ' + str(job.job_title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/job_deleted.txt',
                                         recruiter=recruiter, job=job),
               html_body=render_template('partnership/email/job_deleted.html',
                                         recruiter=recruiter, job=job))

    add_activity(recruiter.user, 21)


def send_email_search_deleted(recruiter, search):
    send_email('Talent Search Deleted: ' + str(search.title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/search_deleted.txt',
                                         recruiter=recruiter, search=search),
               html_body=render_template('partnership/email/search_deleted.html',
                                         recruiter=recruiter, search=search))
    add_activity(recruiter.user, 20)



def send_email_job_deactivated(recruiter, job):
    send_email('Job Posting Deactivated: ' + str(job.job_title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/job_deactivated.txt',
                                         recruiter=recruiter, job=job),
               html_body=render_template('partnership/email/job_deactivated.html',
                                         recruiter=recruiter, job=job))

    add_activity(recruiter.user, 19)



def send_email_search_deactivated(recruiter, search):
    send_email('Talent Search Deactivated: ' + str(search.title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/search_deactivated.txt',
                                         recruiter=recruiter, search=search),
               html_body=render_template('partnership/email/search_deactivated.html',
                                         recruiter=recruiter, search=search))

    add_activity(recruiter.user, 18)



def send_email_job_reactivated(recruiter, job):
    send_email('Job Posting Reactivated: ' + str(job.job_title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/job_reactivated.txt',
                                         recruiter=recruiter, job=job),
               html_body=render_template('partnership/email/job_reactivated.html',
                                         recruiter=recruiter, job=job))

    add_activity(recruiter.user, 17)


def send_email_search_reactivated(recruiter, search):
    send_email('Talent Search Reactivated: ' + str(search.title),
               sender=current_app.config['ADMINS'][0],
               recipients=[recruiter.user.email],
               text_body=render_template('partnership/email/search_reactivated.txt',
                                         recruiter=recruiter, search=search),
               html_body=render_template('partnership/email/search_reactivated.html',
                                         recruiter=recruiter, search=search))

    add_activity(recruiter.user, 16)


def send_email_new_applicant(recruiters, job):
    for recruiter in recruiters:
        send_email('Somebody has applied to your job ' + str(job.job_title),
                   sender=current_app.config['ADMINS'][0],
                   recipients=[recruiter.user.email],
                   text_body=render_template('partnership/email/new_applicant.txt',
                                             recruiter=recruiter, job=job),
                   html_body=render_template('partnership/email/new_applicant.html',
                                             recruiter=recruiter, job=job))
        add_activity(recruiter.user, 15)


def send_email_applicant_removed(job, applicant):
    for recruiter in job.recruiters:
        send_email(str(applicant.name) + ' has withdrawn their application from ' + str(job.job_title),
                   sender=current_app.config['ADMINS'][0],
                   recipients=[recruiter.recruiter.user.email],
                   text_body=render_template('partnership/email/applicant_removed.txt',
                                             recruiter=recruiter.recruiter, job=job, user=applicant.name),
                   html_body=render_template('partnership/email/applicant_removed.html',
                                             recruiter=recruiter.recruiter, job=job, user=applicant.name))
        add_activity(recruiter.user, 29)


def send_email_shared_search(recipient, sender, search):
    send_email(str(sender.name) + ' has added you to a Talent Search',
               sender=current_app.config['ADMINS'][0],
               recipients=[recipient.email],
               text_body=render_template('partnership/email/shared_search.txt',
                                         recipient=recipient, sender=sender, search=search),
               html_body=render_template('partnership/email/shared_search.html',
                                         recipient=recipient, sender=sender, search=search))

    add_activity(recipient, 30)


def send_email_shared_job(recipient, sender, job):
    send_email(str(sender.name) + ' has added you to a Job Posting',
               sender=current_app.config['ADMINS'][0],
               recipients=[recipient.email],
               text_body=render_template('partnership/email/shared_job.txt',
                                         recipient=recipient, sender=sender, job=job),
               html_body=render_template('partnership/email/shared_job.html',
                                         recipient=recipient, sender=sender, job=job))

    add_activity(recipient, 31)
