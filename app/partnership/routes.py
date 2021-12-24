from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.partnership import bp
from app.partnership.forms import RecruiterSearchForm
from app.models import RecruitingAgency,SavedSearch, Candidate, SavedSearchNote, RecruiterSearchAssociation, JobListing
from datetime import datetime
from flask_paginate import Pagination, get_page_args
from app.general import restricted_recruiter, restricted_completed, restricted_recruiter_admin
from app.main.forms import ImageForm, ImageFormMobile
import os
from hashlib import md5
from app.tasks import resize_images


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/partner/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
def partner(id):
    partner = RecruitingAgency.query.filter_by(id=int(id)).first_or_404()
    return render_template('partnership/partner.html', partner=partner)




@bp.route('/saved_search/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
def saved_search(id):
    search = SavedSearch.query.filter_by(id=int(id)).first_or_404()
    # search.apply_results()
    if not search.has_recruiter(current_user.recruiter):
        flash('You may not view job searches that you are not a part of')
        return redirect(url_for('main.user', username=current_user.username))
    if search.recently_shared(current_user):
        flash(str(search.get_creator().user.name) + ' has shared you on this Talent Search')
    search.update_recruiter_association(current_user.recruiter)
    search.recruiters.filter_by(recruiter_id=current_user.recruiter.id).first().last_active = datetime.utcnow()
    search.clear_notifications(current_user)
    return render_template('partnership/saved_search.html', search=search, load_time=datetime.utcnow().strftime("%d%m%Y%H%M%S"))



@bp.route('/job_posting/<id>')
@login_required
@restricted_recruiter
@restricted_completed
def job_posting(id):
    job = JobListing.query.filter_by(id=int(id)).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        flash('You may not view searches that are not assigned to you')
        return redirect(url_for('main.user', username=current_user.username))
    if job.recently_shared(current_user):
        flash(str(job.get_creator().user.name) + ' has shared you on this Job Posting')
    job.update_recruiter_association(current_user.recruiter)
    job.clear_notifications(current_user)
    return render_template('partnership/job_listing.html', job=job)


