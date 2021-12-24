from flask import render_template, flash, redirect, url_for, request, g, jsonify, abort, session, current_app
from flask_login import current_user, login_required
from app import db, login
from app.main import bp
from app.auth.forms import RegistrationForm, MoreInfoRegistration, LoginForm
from app.main.forms import PostForm, CommentForm, ComplaintForm, ImageForm, ImageFormMobile, \
    ReportPost, MessageForm, NewMessageForm, OptInRecruitersForm, JobFoundForm, JobSavedSeaarch
from app.models import User, Forum, Post, Comment, PostReport, CommentReport, Message, \
    Notification, MessageBoard, Industry, JobListing, JobListingActivity, MessageBoardActivity, SuggestedForum, \
    JobSavedSearch, Proximity, Candidate, RecruitingAgency, JobLister, Recruiter, Value, Skill, Background, Hobby,\
    Interest, Resource, ResourceType, State, BlogPost, Event, Appointment
from datetime import datetime, timedelta
from flask_paginate import Pagination, get_page_args
from app.auth.emails import *
from app.main.emails import *
from app.background.emails import *
import requests
import os
from hashlib import md5
import json
from app.general import restricted_user, restricted_completed, restricted_g
from app.tasks import upload_file, resize_images, available_slots
import random
import time

# @celery.task
# def try_celery_testing():
#     with current_app.app_context():
#         send_password_reset_email(User.query.filter_by(id=724).first())


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        if current_user.completed < 2:
            g.more_info_registration = MoreInfoRegistration()
    else:
        g.registration_form = RegistrationForm()
        g.login_form = LoginForm()

    if '.php' in request.path or 'readme.html' in request.path or 'rws/user' in request.path or 'gogs/user' in request.path:
        return render_template('main/intruder.html')


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('main/hompepage.html', title='ILMJTCV')


@bp.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.is_recruiter:
        return render_template('partnership/recruiter.html', title=user.username, user=user)
    else:
        return render_template('main/user.html', title=user.username, user=user)


@bp.route('/forum/<id>', methods=['POST', 'GET'])
@login_required
@restricted_user
@restricted_completed
def forum(id):
    forum = Forum.query.filter_by(id=id).first_or_404()
    return render_template('main/posts/forum.html', forum=forum)


@bp.route('/unemployment_map', methods=['POST', 'GET'])
@login_required
@restricted_user
@restricted_completed
def unemployment_map():
    updated = requests.get('https://ilmjtcv.com/data/mapbox_geojson')
    content = json.loads(updated.content.decode('utf-8'))
    date = datetime.strptime(content['updated'], '%Y-%m-%d %H:%M:%S.%f')
    return render_template('main/map.html', updated=date, title='Map')



@bp.route('/chat', methods=['POST', 'GET'])
@login_required
@restricted_user
@restricted_completed
def chat():
    return render_template('main/posts/chat.html')


@bp.route('/post/<id>', methods=['POST', 'GET'])
@login_required
@restricted_user
@restricted_completed
def post(id):
    post = Post.query.filter_by(id=int(id)).first_or_404()
    return render_template('main/posts/post_page.html', post=post)

# ##############

@bp.route('/terms')
def terms():
    return render_template('main/terms.html', title='Terms')

@bp.route('/community_guidelines')
def community_guidelines():
    return render_template('main/guide_lines.html', title='Community Guidelines')

@bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html', title='Privacy')


@bp.route('/thx')
def thx():
    return render_template('main/thx.html', title='Thank Yous')


@bp.route('/news')
def news():
    return render_template('main/news.html', title='ILMJTCV in the News')


@bp.route('/contact', methods=['POST', 'GET'])
def contact():
    if current_user.is_authenticated:
        form = ComplaintForm()
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.user.data = True

    else:
        form = ComplaintForm()
        form.user.data = False
    if form.validate_on_submit():
        flash(
            'Thank you for submitting an error! We will start de-bugging your issue and be in touch with you soon if we need more information!')
        send_error_email(form)
        return redirect(url_for('main.contact'))

    return render_template('main/contact.html', form=form, title='Contact')


@bp.route('/about')
def about():
    return render_template('main/about.html', title='About')


# @bp.route('/report_post/<type>/<id>', methods=['GET', 'POST'])
# @login_required
# @restricted_user
# def report_post(type, id):
#     if type == '0':
#         post = Post.query.filter_by(id=id).first_or_404()
#         if post.author == current_user:
#             return {'status': 'failed', 'message': 'You may not report your own comments; however, you may delete it.'}
#         form = ReportPost()
#         if form.validate_on_submit():
#             report = PostReport(post_id=post.id, user_id=current_user.id, body=form.body.data,
#                             timestamp=datetime.utcnow(), status=0)
#             db.session.add(report)
#             db.session.commit()
#             send_user_confirmed_report(form.body.data, current_user)
#             total_user_reports_post = PostReport.query.filter_by(user_id=current_user.id).count()
#             total_user_reports_comment = CommentReport.query.filter_by(user_id=current_user.id).count()
#             total_comment_reports = post.reports.count()
#             send_dev_confirmed_report(total_user_reports_post, total_user_reports_comment, total_comment_reports,
#                                       form, current_user)
#             flash("We have received your report and will begin looking into it shortly! We'll be in touch soon!")
#             return redirect(url_for('main.post', id=post.id))
#         return render_template('main/posts/report_post.html', post=post, form=form, comment=None)
#     elif type == '1':
#         comment = Comment.query.filter_by(id=id).first_or_404()
#         post = comment.post
#         if comment.author == current_user:
#             return {'status': 'failed', 'message': 'You may not report your own comments; however, you may delete it.'}
#         form = ReportPost()
#         if form.is_submitted():
#             report = CommentReport(comment_id=comment.id, user_id=current_user.id, body=form.body.data,
#                             timestamp=datetime.utcnow(), status=0)
#             db.session.add(report)
#             db.session.commit()
#             send_user_confirmed_report(form.body.data, current_user)
#             total_user_reports_post = PostReport.query.filter_by(user_id=current_user.id).count()
#             total_user_reports_comment = CommentReport.query.filter_by(user_id=current_user.id).count()
#             total_comment_reports = comment.reports.count()
#             send_dev_confirmed_report(total_user_reports_post, total_user_reports_comment, total_comment_reports,
#                                       form, current_user)
#             flash("We have received your report and will begin looking into it shortly! We'll be in touch soon!")
#             return redirect(url_for('main.post', id=comment.post_id))
#         return render_template('main/posts/report_post.html', comment=comment, post=post, form=form)
#     else:
#         return {'status':'failed', 'message':'Invalid Request'}


@bp.route('/message/<id>', methods=['GET'])
@login_required
def message(id):
    board = MessageBoard.query.filter_by(id=int(id)).first_or_404()
    if current_user not in board.members:
        flash('You do not have access to that message')
        return redirect(url_for('main.messages'))
    activity = current_user.message_boards_activity.filter_by(message_board_id=int(id)).first()
    time = datetime.utcnow()
    activity.last_seen = time + timedelta(seconds=10)
    board.clear_notifications(current_user)
    db.session.commit()
    return render_template('main/messages/board.html', board=board)


@bp.route('/messages', methods=['GET', 'POST'])
@login_required
@restricted_completed
def messages():
    return render_template('main/messages/messages.html')


@bp.route('/job_searches')
@login_required
@restricted_completed
def job_searches():
    if current_user.job_searches.filter_by(status=1).count() > 0:
        return redirect(url_for('main.job_search', id=current_user.job_searches.filter_by(status=1).first().id))
    else:
        return render_template('main/jobs/job_searches.html')

@bp.route('/job_search/<id>')
@login_required
@restricted_completed
def job_search(id):
    search = JobSavedSearch.query.filter_by(id=int(id)).first_or_404()
    # search.get_first_page_results()
    if search.user != current_user:
        flash('You are only allowed to view your own job searches!')
        return redirect(url_for('main.jobs'))
    search.clear_notifications(current_user)
    search.last_checked = datetime.utcnow()
    db.session.commit()
    return render_template('main/jobs/job_ss.html', search=search)


@bp.route('/jobs', methods=['GET', 'POST'])
@bp.route('/jobs/<style>', methods=['GET', 'POST'])
@login_required
@restricted_user
@restricted_completed
def jobs(style=None):
    id = JobSavedSearch.query.filter_by(user_id=current_user.id).first_or_404().id
    return redirect(url_for('main.job_search', id=id))


@bp.route('/recruiting', methods=['GET', 'POST'])
@login_required
@restricted_user
@restricted_completed
def recruiting():
    job_form = JobFoundForm()
    for n in Notification.query.filter_by(user_id=current_user.id, type=2, read=False).all():
        n.read = True
    db.session.commit()
    return render_template('main/jobs/recruiting.html', job_form=job_form)


@bp.route('/professional_profile', methods=['GET', 'POST'])
@login_required
@restricted_user
@restricted_completed
def professional_profile():
    return render_template('main/jobs/professional_profile.html')

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])



@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    forums = current_user.forums
    suggested_forums = current_user.suggested_forums.filter_by(status=0).all()
    recruiter_searches = current_user.candidacies()
    return render_template('main/dashboard.html', suggested_forums=suggested_forums, forums=forums, recruiter_searches=recruiter_searches)

@bp.route('/partnerships', methods=['GET', 'POST'])
def partnerships():
    return render_template('auth/partnership_inquiry2.0.html', title='For Recruiters')


@bp.route('/toggle_r_access', methods=['GET', 'POST'])
@login_required
@restricted_user
@restricted_completed
def toggle_r_access():
    if current_user.recruiter_visibility == 3:
        send_email_recruiting_unenroll(current_user)
        for j in current_user.job_connections_activity.all():
            for k in j.search.recruiters.all():
                n = Notification(user_id=k.recruiter.user_id,
                                 title='Update for ' + str(j.search.title),
                                 sub_title=str(current_user.name) + ' has un-enrolled in recruiter visibility',
                                 link='/p/saved_search/' + str(j.search.id),
                                 type=8,
                                 specific_id=j.search.id)
                db.session.add(n)
        current_user.recruiter_visibility = 4
    elif current_user.recruiter_visibility == 4:
        send_email_recruiting_enroll(current_user)
        current_user.recruiter_visibility = 3
    db.session.commit()
    return redirect(url_for('main.recruiting'))


@bp.route('/current_survey_user')
def current_survey_user():
    return redirect('https://docs.google.com/forms/d/e/1FAIpQLSeIFuVyiNL1eRxS3wIH8a53FMcYUefvP7jBJQxI-eUyGuvzfg/viewform')


@bp.route('/current_survey_recruiter')
def current_survey_recruiter():
    return redirect('https://docs.google.com/forms/d/e/1FAIpQLSeI68d30U8GSfn2VTKw0QCZO1VeXy_xfR93LTSnPUNhKKmY4g/viewform')


# @bp.route('/test5')
# def test5():
#     titles = ['Unemployment Insurance Fact Sheet', 'Disaster Unemployment Assistance', 'Self Employment Assistance', 'Unemployment Insurance Tax']
#     descriptions = ['State financial benefits program for most unemployed workers.', 'Special programs for individuals in disaster areas declared by the President.', 'Special voluntary state programs in a few states for workers starting a business.', 'Information about state and Federal UI tax topics.']
#     links = ['https://oui.doleta.gov/unemploy/docs/factsheet/UI_Program_FactSheet.pdf', 'https://oui.doleta.gov/unemploy/docs/factsheet/DUA_FactSheet.pdf', 'https://oui.doleta.gov/unemploy/docs/factsheet/SEA_FactSheet.pdf', 'https://oui.doleta.gov/unemploy/docs/factsheet/Tax_FactSheet.pdf']
#     for i in range(len(links)):
#         s = Resource(title=titles[i], description=descriptions[i], link=links[i], added=datetime.utcnow(), active=True,
#                      country_id=235, img='https://cdn.countryflags.com/thumbs/united-states-of-america/flag-400.png')
#         db.session.add(s)
#         s.types.append(ResourceType.query.filter_by(id=2).first())
#         db.session.commit()
#     return redirect(url_for('main.index'))

@bp.route('/meet')
@login_required
@restricted_user
def meet():
    return render_template('main/meet_new_people.html')

@bp.route('/resources', methods=['GET'])
@login_required
@restricted_user
def resources():
    num = request.args.get('type') if request.args.get('type') is not None and 0 < int(request.args.get('type')) < 5 else 0
    return render_template('main/mentorship/resources/resources.html', num=int(num))

@bp.route('/blogs')
def blogs():
    return render_template('main/mentorship/blog/blog_base.html')

@bp.route('/events', methods=['GET'])
@login_required
@restricted_user
def events():
    num = request.args.get('type') if request.args.get('type') is not None and 0 < int(request.args.get('type')) < 5 else 0
    return render_template('main/mentorship/events/events.html', num=int(num))

@bp.route('/partners')
@login_required
@restricted_user
def partners():
    return render_template('main/mentorship/partners/partner_base.html')


@bp.route('/blog/<id>')
def blog(id):
    print(id)
    if id == 'wp-admin.php':
        return render_template('main/intruder.html')
    blog = BlogPost.query.filter_by(id=int(id)).first_or_404()
    return render_template('main/mentorship/blog/blog_article.html', blog=blog, title=blog.title, og_img=blog.avatar_meta())

@bp.route('/test9')
def test9():
    a = Resource(link='https://www.benefits.gov/categories', title='Benefits.gov', description='Governmental benefits in areas such as employment/career development, financial assistance, food/nutrition, healthcare, education, etc.', added=datetime.utcnow(), active=True,
                 img='https://cdnmon.cfigroup.com/ueditor/net/upload/image/20170929/6364227796023985614405620.png', country_id=235)
    db.session.add(a)
    a.types.append(ResourceType.query.filter_by(id=2).first())
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/mentorship_preregistration')
def mentorship_preregistration():
    return redirect(url_for('main.sessions'))

@bp.route('/sessions_sign_up')
def sessions_sign_up():
    return render_template('main/mentorship/sessions/pre_registration.html', title='Mentorship Pre-Registration')

@bp.route('/sessions_mentor')
@login_required
@restricted_user
def sessions_mentor():
    return render_template('main/mentorship/sessions/mentor/mentor_home.html', title='Mentorship 1v1')


@bp.route('/sessions')
@login_required
@restricted_user
def sessions():
    return render_template('main/mentorship/sessions/participant/mentee_home.html', title='Mentorship 1v1')

@bp.route('/event_check_in/<id>')
@login_required
@restricted_user
def event_check_in(id):
    e = Event.query.filter_by(id=int(id)).first_or_404()
    if datetime.utcnow() + timedelta(minutes=5) <= e.time_start:
        flash('This event has not started yet. You may check in up to 5 minutes before the listed start time')
        return redirect(url_for('main.events'))
    if datetime.utcnow() - timedelta(minutes=15) >= e.time_end:
        flash('This event is over.')
        return redirect(url_for('main.events'))
    e.check_in(current_user)
    return redirect(e.external_link)

@bp.route('/watch_event/<id>')
@login_required
@restricted_user
def watch_event(id):
    e = Event.query.filter_by(id=int(id)).first_or_404()
    if e.has_passed() and e.recorded:
        e.add_watch(current_user)
        return redirect(e.recorded_link)
    else:
        flash('This event is not available for replay at this time.')
        return redirect(url_for('main.events'))


@bp.route('/test_celery')
@login_required
@restricted_user
def test_celery():
    a = User.query.filter_by(id=1358).first()
    a.delete_user()
    # for a in Appointment.query.all():
    #     #     a.delete_appointment()
    return redirect(url_for('main.index'))


@bp.route('/appointment_check_in/<id>')
@login_required
@restricted_user
def appointment_check_in(id):
    a = Appointment.query.filter_by(id=int(id)).first_or_404()
    if current_user in a.participants:
        a.status = 2
        db.session.commit()
    return redirect(a.get_zoom_link())


@bp.route('/test')
@login_required
@restricted_user
def test():
    r = RecruitingAgency.query.filter_by(id=28).first_or_404()
    r.delete_agency()
    return 'fdsa'