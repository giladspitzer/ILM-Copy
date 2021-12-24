from flask import flash, redirect, url_for, request, render_template
from werkzeug.urls import url_parse
from flask_login import login_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import RegistrationForm, MoreInfoRegistration, LoginForm, PartnershipForm
from app.models import User, Industry, City, MailActivity, RecruitingAgency, Recruiter, JobLister
from app.auth.emails import send_email_edit_profile_changes, send_email_confirm_email, \
    send_email_account_deletion_request, send_email_devs_new_partnership, send_email_partnership_received, \
    send_email_confirm_email_mentor
from app.main.emails import send_email_recruiting_unenroll
import os
from datetime import datetime, timedelta
from random import randint
from app.auth.tasks import check_entered_location
from app.tasks import upload_file, delete_file


# @bp.route('/delete_resume/<id>')
# def delete_resume(id=None):
#     if current_user.is_authenticated:
#         if current_user.resume:
#             delete_file('user', current_user, 'application/pdf', 'resume')
#             current_user.resume = False
#             if current_user.recruiter_visibility == 3:
#                 current_user.recruiter_visibility = 0
#                 current_user.recruiting_bio = None
#                 send_email_recruiting_unenroll(current_user, 1)
#                 flash('Your resume has been deleted and your profile is no longer visible to recruiters')
#             else:
#                 flash('Your resume has been deleted')
#             db.session.add(current_user)
#             db.session.commit()
#             send_email_edit_profile_changes(current_user, [{'field': 'resume',
#                                                             'old': '(previously uploaded)',
#                                                             'new': 'None'}])
#             return redirect(url_for('auth.resume'))
#         else:
#             flash('You do not have a stored resume to delete.')
#             return redirect(url_for('auth.resume'))
#     else:
#         user = User.query.filter_by(id=int(id)).first()
#         if user is None:
#             return redirect(url_for('main.index'))
#         if user.resume:
#             delete_file('user', current_user, 'application/pdf', 'resume')
#             user.resume = False
#             flash('Your resume has been deleted')
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('auth.register2', uid=user.id))


@bp.route('/resume', methods=['POST'])
@login_required
def resume():
    resume = request.files.get('resume')
    extension = None
    if len(resume.filename.split('.')) > 1:
        if resume.filename.split('.')[1] == 'pdf' or resume.filename.split('.')[1] == 'doc' or resume.filename.split('.')[1] == 'docx':
            extension = str(resume.filename.split('.')[1])
    else:
        if resume.content_type == 'application/pdf' or resume.content_type == 'application/docx' or resume.content_type == 'application/doc':
            extension = resume.content_type.split('/')[1]
    if extension is None:
        return {'status': 'failed', 'message':'Something went wrong :(. Please try uploading your resume again.'}
    path = 'app/static/uploads/' + str(current_user.username) + '.pdf'
    os.makedirs('app/static/uploads/', exist_ok=True)
    if extension != 'pdf':
        first_path = 'app/static/uploads/' + str(current_user.username) + '.' + str(extension)
        resume.save(first_path)
    else:
        resume.save(path)
    filename = upload_file(file=path, user=current_user, bucket='user', extension='application/pdf', name='resume')
    os.remove(path=path)
    current_user.directory = filename
    current_user.resume = True
    db.session.commit()
    return {'status': 'success'}
    # try:
    #     resume = request.files.get('resume')
    #     print(resume.content_type)
    #     first_path = 'app/static/uploads/' + str(current_user.username) + '_resume'
    #     path = 'app/static/uploads/' + str(current_user.username) + '.pdf'
    #     os.makedirs('app/static/uploads/', exist_ok=True)
    #     resume.save(first_path)
    #     convert(first_path, path)
    #     filename = upload_file(file=path, user=current_user, bucket='user', extension='application/pdf', name='resume')
    #     os.remove(path=path)
    #     current_user.directory = filename
    #     current_user.resume = True
    #     db.session.commit()
    #     return {'status': 'success'}
    # except:
    #     return {'status': 'failed', 'message':'Something went wrong :(. Please try uploading your resume again.'}


@bp.route('/get_register_numbers', methods=['POST'])
def get_register_numbers():
    industry = Industry.query.filter_by(title=str(request.form.get('i'))).count()
    location = City.query.filter_by(name=str(request.form.get('l').split(',')[0])).count()
    if industry == 0 and location == 1:
        if City.query.filter_by(name=str(request.form.get('l').split(',')[0])).first().jobs.count() > 0:
            count = City.query.filter_by(name=str(request.form.get('l').split(',')[0])).first().jobs.count()
        else:
            count = randint(119, 3425)

    elif industry == 1 and location == 0:
        if len(Industry.query.filter_by(title=str(request.form.get('i'))).first().jobs) > 0:
            count = len(Industry.query.filter_by(title=str(request.form.get('i'))).first().jobs)
        else:
            count = randint(119, 3425)

    else:
        count = str(randint(119, 3425))
    return {'status': 'success', 'html': render_template('auth/register.html', title='Register', j=count, r=str(randint(3, 11)), special=True),
            'title': 'Register', 'url': '/auth/register'}


@bp.route('/verify_unique', methods=['POST'])
@bp.route('/verify_unique/<id>', methods=['POST'])
def verify_unique(id=None):
    if current_user.is_authenticated:
        content = {'u': True, 'e': True}
        if id is not None:
            user = Recruiter.query.filter_by(id=int(id)).first_or_404().user
            if User.query.filter_by(username=str(request.form.get('u'))).count() > 0:
                if User.query.filter_by(username=str(request.form.get('u'))).first() != user:
                    content['u'] = False
            if User.query.filter_by(email=str(request.form.get('e'))).count() > 0:
                if User.query.filter_by(email=str(request.form.get('e'))).first() != user:
                    content['e'] = False
        else:
            if User.query.filter_by(username=str(request.form.get('u'))).count() > 0:
                if User.query.filter_by(username=str(request.form.get('u'))).first() != current_user:
                    content['u'] = False
            if User.query.filter_by(email=str(request.form.get('e'))).count() > 0:
                if User.query.filter_by(email=str(request.form.get('e'))).first() != current_user:
                    content['e'] = False
        return content
    else:
        content = {'u': True, 'e': True}
        if User.query.filter_by(username=str(request.form.get('u'))).count() > 0:
            content['u'] = False
        if User.query.filter_by(email=str(request.form.get('e'))).count() > 0:
            content['e'] = False
        return content


@bp.route('/send_new_confirmation_email', methods=['POST'])
def send_new_confirmation_email():
    if current_user.email_verified:
        return {'status': 'error',
                'message': 'You have already confirmed your email. Contact us to troubleshoot this issue.'}
    else:
        last = MailActivity.query.filter_by(user_id=current_user.id, type=0).order_by(
            MailActivity.timestamp.desc()).first()
        if last is not None and last.timestamp + timedelta(minutes=5) <= datetime.utcnow():
            send_email_confirm_email(current_user)
            return {'status': 'success', 'message': 'Email Sent'}
        else:
            return {'status': 'error', 'message': 'You must wait 5 minutes between sending confirmation emails.'}


@bp.route('/register_submit', methods=['POST'])
def register_submit():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, is_recruiter=False,
                    password_length=len(form.password.data) * '*', completed=1, created=datetime.utcnow(),
                    email_verified=False, recruiter_visibility=0)
        user.set_password(form.password.data)
        user.add_forums()
        db.session.add(user)
        db.session.commit()
        print(request.form)
        if form.mentor.data:
            user.intended_mentor = True
            db.session.commit()
            send_email_confirm_email_mentor(user)
            login_user(user)
            return {'status': 'success', 'url': str(url_for('main.sessions_mentor'))}
        else:
            send_email_confirm_email(user)
            login_user(user)
            return {'status': 'success', 'url': str(url_for('main.unemployment_map', username=user.username))}
    else:
        return {'status': 'failed', 'message': 'An error has occurred. Please try again.'}


@bp.route('/submit_more_info', methods=['POST'])
def submit_more_info():
    if current_user.completed < 2:
        print(request.form)
        user_codes = check_entered_location(int(request.form.get('country')), str(request.form.get('city')), str(request.form.get('zip')))
        if user_codes is None:
            return {'status': 'failed', 'message': 'An error has occurred with your location input. Please try again.'}
        current_user.set_location(user_codes)
        current_user.industry_id = int(request.form.get('industry'))
        current_user.completed = 2
        db.session.commit()
        current_user.add_first_job_ss()
        current_user.suggest_forums()
        return {'status': 'success', 'url': request.referrer}
    else:
        return {'status': 'failed', 'message': 'Account already confirmed'}


@bp.route('/log_in_', methods=['POST'])
def log_in_():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return {'status':'error', 'message':'Invalid username or password'}
        else:
            login_user(user, remember=form.remember_me.data)
            try:
                print(request.referrer)
                next_page = str(request.referrer).replace('%2F', '/').split('?next=')[1].replace('%3F', '?').replace('%3D', '=')
            except IndexError:
                next_page = url_for('main.user', username=current_user.username)
            return {'status': 'success', 'url': next_page}
    else:
        return {'status': 'error', 'message': 'Invalid username or password'}


@bp.route('/partnership_inquiry_submit', methods=['POST'])
def partnership_inquiry_submit():
    try:
        # if RecruitingAgency.query.filter_by(name=str(request.form.get('company'))).count() > 0:
        #     return {'status': 'failed', 'message': 'There is already a registered recruiter entity with that company name. Please try again or reach out to use if you have further questions.'}
        if User.query.filter_by(email=str(request.form.get('email'))).count() > 0:
            return {'status': 'failed', 'message': 'A user with that email already exists. You must use a unique email to enroll as a recruiter.'}
        r = RecruitingAgency(name=str(request.form.get('company')), website=str(request.form.get('link')),
                             date_requested=datetime.utcnow(), status=1, request_name=str(request.form.get('name')),
                             request_email=str(request.form.get('email')), additional_info=str(request.form.get('additional_info')))
        db.session.add(r)
        db.session.commit()
        l = JobLister(website=str(request.form.get('link')), agency_id=r.id)
        db.session.add(l)
        db.session.commit()
        user = User(email=str(r.request_email), name=str(r.request_name), is_recruiter=True, completed=0)
        db.session.add(user)
        db.session.commit()
        recruiter = Recruiter(user_id=user.id, agency_id=r.id, admin=2, status=0)
        db.session.add(recruiter)
        db.session.commit()
        send_email_partnership_received(r)
        send_email_devs_new_partnership(r)
        return {'status': 'success', 'message': 'Thank you for for your interest in partnering with ILMJTCV. We will be in touch with you as we review your application. You are now being redirected'}
    except:
        return {'status': 'failed', 'message': 'An error has occurred. Please try again.'}


@bp.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
    try:
        send_email_account_deletion_request(current_user)
        return {'status': 'success', 'message': 'Please check your email for further instructions'
                                                'as to how to delete your account.'}
    except:
        return {'status': 'failed'}