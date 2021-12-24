from flask import flash, redirect, url_for, render_template
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.main.forms import PostForm, CommentForm, ComplaintForm, ImageForm, ImageFormMobile, MessageForm, \
    NewMessageForm, OptInRecruitersForm, JobFoundForm, JobSavedSeaarch
from app.models import User, Forum, Post, Comment, MessageBoard, Industry, JobListing, JobListingActivity, \
    SuggestedForum, JobSavedSearch, Proximity
from datetime import datetime, timedelta
from flask_paginate import Pagination, get_page_args
import requests
import json
from app.general import restricted_user, restricted_completed



@bp.route('/terms_', methods=['GET'])
def terms_():
    return {'html': render_template('main/terms.html'), 'title': 'Terms', 'url': '/terms'}


@bp.route('/privacy_', methods=['GET'])
def privacy_():
    return {'html': render_template('main/privacy.html'), 'title': 'Privacy', 'url': '/privacy'}


@bp.route('/contact_', methods=['GET'])
def contact_():
    if current_user.is_authenticated:
        form = ComplaintForm()
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.user.data = True
    else:
        form = ComplaintForm()
        form.user.data = False
    return {'html': render_template('main/contact.html', form=form), 'title': 'Contact', 'url': '/contact'}


@bp.route('/about_', methods=['GET'])
def about_():
    return {'html': render_template('main/about.html'), 'title': 'About', 'url': '/about'}


@bp.route('/_', methods=['GET'])
def index_():
    # print(render_template('main/hompepage.html'))
    return {'html': render_template('main/hompepage.html', title='ILMJTCV'), 'title': 'ILMJTCV',
            'url': '/'}


@bp.route('/user_/<username>', methods=['GET'])
@login_required
def user_(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = ImageForm()
    form_mobile = ImageFormMobile()
    if user.is_recruiter:
        return {'html': render_template('partnership/recruiter.html', title=user.username, user=user, form=form, form_mobile=form_mobile), 'title': user.username, 'url': '/user/' + str(user.username)}

    else:
        return {'html': render_template('main/user.html', title=user.username, user=user, form=form, form_mobile=form_mobile), 'title': user.username, 'url': '/user/' + str(user.username)}


@bp.route('/forum_/<id>/<style>', methods=['GET'])
@bp.route('/forum_/<id>', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def forum_(id, style='a'):
    if style == 'a':
        return redirect(url_for('main.forum', id=id, style=0))
    forum = Forum.query.filter_by(id=id).first_or_404()
    if current_user not in forum.users:
        flash('You are not apart of the requested forum')
        return redirect(url_for('main.chat'))
    form = PostForm()
    if style == '0':
        pre_posts = forum.posts.filter_by(deleted=0).order_by(Post.timestamp.desc()).all()
    elif style == '1':
        unsorted_posts = forum.posts.order_by(Post.timestamp.desc()).all()
        pre_posts = sorted(unsorted_posts, key=lambda r: r.comments.count(), reverse=True)
    else:
        pre_posts = []

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(pre_posts)
    posts = pre_posts[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap3')
    return {
        'html': render_template('main/forum.html', forum=forum, form=form, posts=posts,
                           per_page=per_page, pagination=pagination),
        'title': forum.title, 'url': '/forum/' + str(forum.id)}


@bp.route('/unemployment_map_', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def unemployment_map_():
    updated = requests.get('https://ilmjtcv.com/data/mapbox_geojson')
    content = json.loads(updated.content.decode('utf-8'))
    date = datetime.strptime(content['updated'], '%Y-%m-%d %H:%M:%S.%f')
    return {
        'html': render_template('main/map.html', updated=date, title='Map'),
        'title': 'Map', 'url': '/unemployment_map'}


@bp.route('/chat_/forum/<id>/<style>', methods=['GET'])
@bp.route('/chat_/forum/<id>', methods=['GET'])
@bp.route('/chat_', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def chat_(id=0, style='a'):
    if len(current_user.forums) > 0:
        if id == 0:
            forum = current_user.forums[0]
            return redirect(url_for('main.chat', id=forum.id, style=0))
        else:
            forum = next((x for x in current_user.forums if x.id == int(id)), current_user.forums[0])
            if style == 'a':
                return redirect(url_for('main.chat', id=forum.id, style=0))

        form = PostForm()
        if style == '0':
            pre_posts = forum.posts.filter_by(deleted=0).order_by(Post.timestamp.desc()).all()
        elif style == '1':
            unsorted_posts = forum.posts.filter_by(deleted=0).order_by(Post.timestamp.desc()).all()
            pre_posts = sorted(unsorted_posts, key=lambda r: r.comments.count(), reverse=True)
        else:
            pre_posts = []

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')
        total = len(pre_posts)
        posts = pre_posts[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap3')
    else:
        if id != 0:
            redirect(url_for('main.chat'))
        forum = None
        form = None
        posts = None
        per_page = None
        pagination = None
    suggested = SuggestedForum.query.filter(SuggestedForum.user_id == current_user.id, SuggestedForum.status < 2).all()
    return {
        'html': render_template('main/chat.html', current_forum=forum, form=form, posts=posts,
                           per_page=per_page, pagination=pagination, suggested=suggested, title='Chat'),
        'title': 'Chat', 'url': '/chat/' + str(forum.id) + '/' + str(style)}


@bp.route('/post_/<id>/<style>', methods=['GET'])
@bp.route('/post_/<id>', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def post_(id, style='a'):
    if style == 'a':
        return redirect(url_for('main.post', id=id, style=0))
    post = Post.query.filter_by(id=int(id)).first_or_404()
    if post.forum_id not in [forum.id for forum in current_user.forums]:
        flash('You do not have access to view that post')
        return redirect(url_for('main.chat'))
    form = CommentForm()
    if style == '0':
        pre_comments = post.comments.filter_by(deleted=0).order_by(Comment.timestamp.desc()).all()
    elif style == '1':
        pre_comments = post.comments.filter_by(deleted=0).all()
        pre_comments = sorted(pre_comments, key=lambda r: r.votes.count(), reverse=True)
    else:
        comments = []
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(pre_comments)
    comments = pre_comments[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap3')
    return {
        'html': render_template('main/posts/post_page.html', post=post, form=form, comments=comments,
                           per_page=per_page, pagination=pagination),
        'title': 'Post', 'url': '/post/'+ str(post.id) +'/' + str(style)}


@bp.route('/message_/<id>', methods=['GET'])
@login_required
def message_(id):
    board = MessageBoard.query.filter_by(id=int(id)).first_or_404()
    if current_user not in board.members:
        flash('You do not have access to that message')
        return redirect(url_for('main.messages'))
    activity = current_user.message_boards_activity.filter_by(message_board_id=int(id)).first()
    time = datetime.utcnow()
    activity.last_seen = time + timedelta(seconds=10)
    db.session.commit()
    form = MessageForm()
    messages = board.messages
    return {
        'html': render_template('main/messages/board.html', board=board, form=form, messages=messages),
        'title': board.subject, 'url': '/message/' + str(board.id)}


@bp.route('/messages_', methods=['GET'])
@login_required
@restricted_completed
def messages_():
    messages = sorted(current_user.message_boards, key= lambda r : r.last_active, reverse=True)
    form = NewMessageForm()
    return {
        'html': render_template('main/messages/messages.html', messages=messages, form=form),
        'title': 'Messages', 'url': '/messages'}


@bp.route('/job_search_/<id>', methods=['GET'])
@login_required
@restricted_completed
def job_search_(id):
    search = JobSavedSearch.query.filter_by(id=int(id)).first_or_404()
    if search.user != current_user:
        flash('You are only allowed to view your own job searches!')
        return redirect(url_for('main.jobs'))
    if search.status != 1:
        flash('The requested search has been deactivated.')
        return redirect(url_for('main.jobs'))
    search.last_checked = datetime.utcnow()
    db.session.commit()
    if Industry.query.filter_by(id=4).first() in search.industries:
        flash('We applogize for any jobs that are not relevant to you. We are working on better tailoring jobs in the education industry.')
    applied = db.session.query(JobListing).join(JobListingActivity).filter(
        JobListing.id == JobListingActivity.job_id,
        JobListingActivity.status == 3,
        JobListingActivity.search_id == search.id
    ).order_by(JobListingActivity.order.asc()).all()
    viewed = db.session.query(JobListing).join(JobListingActivity).filter(
        JobListing.id == JobListingActivity.job_id,
        JobListingActivity.status == 1,
        JobListingActivity.search_id == search.id
    ).order_by(JobListingActivity.order.asc()).all()
    considering = db.session.query(JobListing).join(JobListingActivity).filter(
        JobListing.id == JobListingActivity.job_id,
        JobListingActivity.status == 2,
        JobListingActivity.search_id == search.id
    ).order_by(JobListingActivity.order.asc()).all()
    uninterested = db.session.query(JobListing).join(JobListingActivity).filter(
        JobListing.id == JobListingActivity.job_id,
        JobListingActivity.status == -1,
        JobListingActivity.search_id == search.id
    ).order_by(JobListingActivity.order.asc()).all()
    pre_jobs = db.session.query(JobListing).join(JobListingActivity).filter(
        JobListing.id == JobListingActivity.job_id,
        JobListingActivity.status == 0,
        JobListingActivity.search_id == search.id
    ).order_by(JobListingActivity.order.asc()).all()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(pre_jobs)
    jobs = pre_jobs[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap3')
    return {
        'html': render_template('main/jobs/job_ss.html', jobs=jobs, per_page=per_page, pagination=pagination,
                           applied=applied, viewed=viewed, considering=considering, uninterested=uninterested,
                           search=search),
        'title': search.title, 'url': '/job_search/' + str(search.id)}


@bp.route('/jobs_', methods=['GET'])
@bp.route('/jobs_/<style>', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def jobs_(style=None):
    form = JobSavedSeaarch()
    form.proximity.choices = [(x.id, x.title) for x in Proximity.query.all()]
    if style is None:
        style = '1'
    if style == '0':
        searches = current_user.job_searches.filter_by(status=0).all()
    else:
        searches = current_user.job_searches.filter_by(status=1).all()
    job_form = JobFoundForm()
    return {
        'html': render_template('main/jobs/jobs2.0.html', form=form, job_form=job_form, searches=searches, type=int(style), title='Jobs'),
        'title': 'Jobs', 'url': '/jobs/' + str(style)}


@bp.route('/recruiting_', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def recruiting_():
    job_form = JobFoundForm()
    return {
        'html': render_template('main/jobs/recruiting.html', job_form=job_form, title='Recruiting'),
        'title': 'Recruiting', 'url': '/recruiting'}


@bp.route('/partnerships_', methods=['GET'])
def partnerships_():
    if current_user.is_authenticated:
        flash('You must logout to view that page')
        return {'html': render_template('main/hompepage.html', title='ILMJTCV'), 'title': 'ILMJTCV', 'url': '/'}
    else:
        return {'html': render_template('auth/partnership_inquiry2.0.html', title='For Recruiters'), 'title': 'ILMJTCV Recruiting', 'url': '/partnerships'}