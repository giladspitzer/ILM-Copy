from flask import flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from app import db
from app.partnership import bp
from app.partnership.emails import send_email_confirm_recruiter, send_email_new_job_posting_quick, \
    send_email_new_job_posting, send_email_job_deleted, send_email_job_deactivated, send_email_job_reactivated, \
    send_email_search_deleted, send_email_search_deactivated, send_email_search_reactivated, send_email_shared_search, \
    send_email_shared_job
from app.models import Recruiter, SavedSearch, Candidate, \
    Experience, User, ResumeView, SavedSearchNote, CandidateNote, MessageBoardActivity, MessageBoard, Message, \
    Notification, RecruitingAgency, JobListing, Industry, JobPostingNote, QuickApplyProfile, Applicant, \
    ApplicantNote, RecruiterSearchAssociation, RecruiterJobAssociation
from datetime import datetime, timedelta
from app.general import restricted_recruiter, restricted_completed, restricted_recruiter_admin
from app.auth.emails import send_email_confirm_new_email, send_email_edit_profile_changes
from app.main.emails import send_email_job_no_longer_available, send_email_job_available_again
import os
from hashlib import md5
from app.tasks import check_location, add_locations, resize_images

@bp.route('/resend_recruiter_activation/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
@restricted_recruiter_admin
def resend_recruiter_activation(id):
    recruiter = Recruiter.query.filter_by(id=int(id)).first_or_404()
    if recruiter.status == 0:
        send_email_confirm_recruiter(recruiter)
        flash(str(recruiter.user.name) + " has been sent another activation email.")
    else:
        flash('This recruiter has already activated their account.')

    return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))



@bp.route('/deactivate_recruiter/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
@restricted_recruiter_admin
def deactivate_recruiter(id):
    recruiter = Recruiter.query.filter_by(id=int(id)).first_or_404()
    if recruiter.status != -1:
        recruiter.status = -1
        db.session.commit()
        flash(str(recruiter.user.name) + "'s account has been de-activated")
    else:
        flash(str(recruiter.user.name) + "'s account has been de-activated")
    return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))


@bp.route('/activate_recruiter/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
@restricted_recruiter_admin
def activate_recruiter(id):
    recruiter = Recruiter.query.filter_by(id=int(id)).first_or_404()
    if recruiter.status != 1:
        recruiter.status = 1
        db.session.commit()
        flash(str(recruiter.user.name) + "'s account has been activated")
    else:
        flash(str(recruiter.user.name) + "'s account has been activated")
    return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))


@bp.route('/update_recruiter', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
@restricted_recruiter_admin
def update_recruiter():
    id = request.form.get('id')
    username = str(request.form.get('username'))
    email = str(request.form.get('email'))
    experience = int(request.form.get('experience'))
    title = str(request.form.get('title'))
    authority = int(request.form.get('authority'))
    name = str(request.form.get('name'))

    recruiter = Recruiter.query.filter_by(id=int(id)).first_or_404()
    user_by_username = User.query.filter_by(username=username).first()
    if user_by_username is not None and user_by_username != recruiter.user:
        flash('The username "' + str(username) + '" is already in use. Please enter a different one.')
        return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))

    user_by_email = User.query.filter_by(email=email).first()
    if user_by_email is not None and user_by_email != recruiter.user:
        flash(
            'The email address "' + str(email) + '" is already in use. Please enter a different one.')
        return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))

    def get_changes(name, username, email, experience, title, authority):
        changes = []
        if email != recruiter.user.email:
            changes.append({'field': 'name',
                            'old': recruiter.user.name,
                            'new': name})
        if email != recruiter.user.email:
            changes.append({'field': 'email',
                            'old': recruiter.user.email,
                            'new': email})
        if username != recruiter.user.username:
            changes.append({'field': 'username',
                            'old': recruiter.user.username,
                            'new': username})
        if experience != recruiter.user.experience_id:
            changes.append({'field': 'experience',
                            'old': recruiter.user.experience.title,
                            'new': Experience.query.filter_by(id=int(experience)).first().title})
        if title != recruiter.user.position_title:
            changes.append({'field': 'title',
                            'old': recruiter.user.position_title,
                            'new': title})
        if recruiter.status != 2:
            if authority != recruiter.status:
                if authority == 1 and recruiter.status == 0:
                    changes.append({'field': 'authority',
                                    'old': 'recruiter',
                                    'new': 'admin'})
                elif authority == 0 and recruiter.status == 1:
                    changes.append({'field': 'authority',
                                    'old': 'admin',
                                    'new': 'recruiter'})

        return changes

    changes = get_changes(name, username, email, experience, title, authority)

    send_email_edit_profile_changes(recruiter.user, changes)

    recruiter.user.username = username
    recruiter.user.name = name

    recruiter.user.experience_id = int(experience)
    recruiter.user.position_title = title
    if recruiter.admin != 2:
        recruiter.admin = int(authority)

    if recruiter.user.email != email:
        recruiter.user.email = email
        recruiter.user.email_verified = False
        flash(str(username) + 's profile has been updated and they have been notified. They will need to confirm their new email before using their account.')
        send_email_confirm_new_email(recruiter.user)
    else:
        flash(str(username) + 's profile has been updated and they have been notified.')

    db.session.commit()

    return {'status': 'success'}


@bp.route('/add_recruiter', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
@restricted_recruiter_admin
def add_recruiter():
    email = str(request.form.get('email'))
    experience = int(request.form.get('experience'))
    title = str(request.form.get('title'))
    authority = int(request.form.get('authority'))
    name = str(request.form.get('name'))

    user_by_email = User.query.filter_by(email=email).count()
    if user_by_email > 0:
        flash(
            'The email address "' + str(email) + '" is already in use. Please enter a different one.')
        return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))

    user = User(email=str(email), name=str(name), is_recruiter=True, completed=0, experience_id=experience, position_title=title)
    db.session.add(user)
    db.session.commit()
    recruiter = Recruiter(user_id=user.id, agency_id=current_user.recruiter.agency_id, admin=authority, status=0)
    db.session.add(recruiter)
    db.session.commit()
    send_email_confirm_recruiter(recruiter)
    flash("A recruiter account has been added for " + str(request.form.get('email')) + '. They will receive email instructions about how to finalize their registration.')
    return {'status': 'success'}


@bp.route('/terminate_search/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
def terminate_search(id):
    search = SavedSearch.query.filter_by(id=int(id)).first_or_404()
    if current_user.recruiter not in search.get_recruiters():
        flash('You are not allowed to terminate this search')
        return redirect(url_for('partnership.saved_search', id=int(id)))
    search.terminate()
    search.update_recruiter_association(current_user.recruiter)
    return redirect(url_for('partnership.recruiter_search'))


@bp.route('/activate_search/<id>', methods=['GET', 'POST'])
@login_required
@restricted_recruiter
@restricted_completed
def activate_search(id):
    search = SavedSearch.query.filter_by(id=int(id)).first_or_404()
    if current_user.recruiter not in search.get_recruiters():
        flash('You are not allowed to activate this search')
        return redirect(url_for('partnership.saved_search', id=int(id)))
    search.activate()
    search.update_recruiter_association(current_user.recruiter)
    return redirect(url_for('partnership.recruiter_search'))


@bp.route('/edit_search_activity/<candidate>/<direction>')
@login_required
@restricted_recruiter
@restricted_completed
def edit_search_activity(candidate, direction):
    activity = Candidate.query.filter_by(id=int(candidate)).first_or_404()  # fix
    if current_user.recruiter not in activity.search.get_recruiters():
        flash('You are not allowed to edit this candidate')
        return redirect(url_for('partnership.saved_search', id=int(activity.search.id)))
    if int(direction) <= 4 and int(direction) >= 0:
        if Candidate.query.filter_by(search_id=activity.search_id, status=int(direction)).count() > 0:
            last_order = Candidate.query.filter_by(search_id=activity.search_id, status=int(direction)).order_by(Candidate.order.asc()).first().order
        else:
            for o in Candidate.query.filter_by(search_id=activity.search_id, status=int(activity.status)).all():
                if o.order > activity.order:
                    o.order -= 1
            last_order = 0
        activity.order = last_order + 1
        activity.status = int(direction)
    else:
        flash('Error Occurred')
    db.session.commit()
    return redirect(url_for('partnership.saved_search', id=int(activity.search_id)))


@bp.route('/new_search_activity/<candidate>/<direction>/<search>')
@login_required
@restricted_recruiter
@restricted_completed
def new_search_activity(candidate, direction, search):
    the_search = SavedSearch.query.filter_by(id=int(search)).first_or_404()
    if current_user.recruiter not in the_search.get_recruiters():
        flash('You are not allowed to edit this candidate')
        return redirect(url_for('partnership.saved_search', id=int(search)))
    if Candidate.query.filter_by(user_id=int(candidate), search_id=int(search)).count() > 0:
        new = Candidate.query.filter_by(user_id=int(candidate), search_id=int(search)).first()
        new.status = 1
    else:
        new = Candidate(user_id=int(candidate), status=int(direction), search_id=int(search))
    db.session.add(new)
    db.session.commit()
    return redirect(url_for('partnership.saved_search', id=int(search)))


@bp.route('view_resume/<uid>/<option>')
@login_required
@restricted_recruiter
@restricted_completed
def view_resume(uid, option=0):
    if int(option) == 0:
        candidate = Candidate.query.filter_by(id=int(uid)).first_or_404()
        if candidate.user.recruiter_visibility == 3 and candidate.user.resume:
            c = ResumeView(recruiter_id=current_user.recruiter.id, user_id=candidate.user_id, timestamp=datetime.utcnow(),
                           search_id=candidate.search_id)
            db.session.add(c)
            db.session.commit()
            return redirect(candidate.user.get_resume())
    elif int(option) == 1:
        applicant = Applicant.query.filter_by(id=int(uid)).first_or_404()
        if applicant.user.recruiter_visibility == 3 and applicant.user.resume:
            c = ResumeView(recruiter_id=current_user.recruiter.id, user_id=applicant.user_id,
                           timestamp=datetime.utcnow(),
                           applicant_id=applicant.id)
            db.session.add(c)
            db.session.commit()
            return redirect(applicant.user.get_resume())
    else:
        flash('The requested resume is unavailable')
        return redirect(url_for('partnership.recruiter_search'))


@bp.route('/change_order/<id>/', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def change_order(id):
    search = SavedSearch.query.filter_by(id=int(id)).first_or_404()
    removed = request.form.getlist('q[0][]')
    candidates = request.form.getlist('q[1][]')
    considering = request.form.getlist('q[2][]')
    strongly = request.form.getlist('q[3][]')
    categories = [removed, candidates, considering, strongly]
    for c in range(len(categories)):
        if len(categories[c]) > 0 and categories[c][0] != '':
            for i in range(len(categories[c])):
                ca = Candidate.query.filter_by(search_id=search.id, status=int(c), id=int(categories[c][i].split('_')[1])).first()
                ca.order = int(i) + 1
                db.session.add(ca)
                db.session.commit()
    return jsonify('success')


@bp.route('/post_search_note', methods=['POST'])
@login_required
@restricted_recruiter
def post_search_note():
    s_id = request.form.get('id')
    search = SavedSearch.query.filter_by(id=int(s_id)).first_or_404()
    if not search.has_recruiter(current_user.recruiter):
        return abort(403)
    note = SavedSearchNote(body=str(request.form.get('q')), recruiter_id=current_user.recruiter.id, search_id=search.id,
                           timestamp=datetime.utcnow())
    db.session.add(note)
    db.session.commit()
    search.update_recruiter_association(current_user.recruiter)
    html = note.render_html()
    return {'status': 'success', 'html': html}


@bp.route('/post_job_posting_note', methods=['POST'])
@login_required
@restricted_recruiter
def post_job_note():
    j_id = request.form.get('id')
    job = JobListing.query.filter_by(id=int(j_id)).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        return abort(403)
    note = JobPostingNote(body=str(request.form.get('q')), recruiter_id=current_user.recruiter.id, job_id=job.id,
                           timestamp=datetime.utcnow())
    db.session.add(note)
    db.session.commit()
    job.update_recruiter_association(current_user.recruiter)
    html = note.render_html()
    return {'status': 'success', 'html': html}


@bp.route('/post_candidate_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def post_candidate_note():
    candidate = Candidate.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not candidate.search.has_recruiter(current_user.recruiter):
        return abort(403)
    note = CandidateNote(body=str(request.form.get('q')), recruiter_id=current_user.recruiter.id, candidate_id=candidate.id,
                           timestamp=datetime.utcnow())
    db.session.add(note)
    db.session.commit()
    candidate.search.update_recruiter_association(current_user.recruiter)

    html = note.render_html()
    return {'status':'success', 'html': html}

@bp.route('/post_applicant_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def post_applicant_note():
    applicant = Applicant.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not applicant.application.job.has_recruiter(current_user.recruiter):
        return abort(403)
    note = ApplicantNote(body=str(request.form.get('q')), recruiter_id=current_user.recruiter.id, applicant_id=applicant.id,
                           timestamp=datetime.utcnow())
    db.session.add(note)
    db.session.commit()
    applicant.application.job.update_recruiter_association(current_user.recruiter)

    html = note.render_html()
    return {'status':'success', 'html': html}


@bp.route('/change_search_visibility', methods=['POST', 'GET'])
@login_required
@restricted_recruiter
@restricted_completed
def change_search_visibility():
    search = SavedSearch.query.filter_by(id=int(request.form.get('i'))).first_or_404()
    if not search.has_recruiter(current_user.recruiter):
        return {'status': 'error', 'message': 'you may only edit your own searches'}
    search.update_recruiter_association(current_user.recruiter)

    d = request.form.get('d')
    if int(d) == 1:
        search.public = True
    elif int(d) == 0:
        search.public = False
    db.session.commit()
    return {'status': 'success'}


@bp.route('/update_message_activity', methods=['POST', 'GET'])
@login_required
@restricted_recruiter
@restricted_completed
def update_message_activity():
    candidate = Candidate.query.filter_by(id=int(request.form.get('c'))).first_or_404()
    board = candidate.message_board.first_or_404()
    if current_user not in board.members:
        abort(403)
    candidate.search.update_recruiter_association(current_user.recruiter)
    candidate.clear_notifications(current_user)
    activity = board.activity.filter_by(user_id=current_user.id).first_or_404()
    activity.last_seen = RecruiterSearchAssociation.query.filter_by(search_id=candidate.search_id,
                                                    recruiter_id=current_user.recruiter.id).first_or_404().last_active
    board.clear_notifications(current_user)
    db.session.commit()

    return {'status': 'success'}


@bp.route('/send_candidate_message', methods=['POST', 'GET'])
@login_required
@restricted_recruiter
@restricted_completed
def send_candidate_message():
    candidate = Candidate.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not candidate.search.has_recruiter(current_user.recruiter):
        return {'status': 'failed', 'message':'You are not allowed to edit this search'}
    candidate.search.update_recruiter_association(current_user.recruiter)
    candidate.clear_notifications(current_user)
    if candidate.message_board.first() is None:
        # create board for candidate, add participants, and send message
        subject = "'" + str(candidate.search.title) + "' ~~ " + str(candidate.user.name)
        board = MessageBoard(subject=subject, last_active=datetime.utcnow(), recruiting=True,
                         candidate_id=candidate.id)  # create board
        db.session.add(board)
        db.session.commit()
        for r in candidate.search.recruiters:
            board.add_member(r.recruiter.user)
        board.add_member(candidate.user)
        board.send_message(current_user, message=str(request.form.get('q')))
    else:
        board = candidate.message_board.first()
        board.send_message(current_user, message=str(request.form.get('q')))
    html = ''
    for i in board.get_messages(0, 0)[::-1]:
        html += i.render_html()
    return {'status': 'success', 'html':html}

@bp.route('/add_recruiter_search', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def add_recruiter_search():
        title = request.form.get('title')
        description = request.form.get('description')
        industry = request.form.get('industry')
        l_specific = False if request.form.get('remote') == 'true' else True
        city = request.form.get('city')
        public = True if request.form.get('public') == 'true' else False
        if l_specific:
            data = check_location(city.split(',')[0])  # check their entered data
            if data == {}:
                return {'status': 'error', 'message':'An error has occured relating to your location input. Please try again.'}
            if 'city' not in list(data.keys()):  # if no postal code then return redirect
                return {'status': 'error', 'message':'An error has occured relating to your location input. Please try again.'}
            user_codes = add_locations(3, data)
            city_id = int(user_codes['city'])
        else:
            city_id = None
        search = SavedSearch(title=str(title), snippet=str(description),
                             industry_id=int(industry), city_id=city_id,
                             status=1, last_updated=datetime.utcnow(), public=public,
                             agency_id=current_user.recruiter.agency_id, l_specific=l_specific)
        db.session.add(search)
        db.session.commit()
        search.add_initial_recruiters(current_user)
        search.apply_results()
        return {'status': 'success', 'id': str(search.id)}


@bp.route('/edit_recruiter_search', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_recruiter_search():
    search = SavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not search.has_recruiter(current_user.recruiter):
        abort(403)
    search.update_recruiter_association(current_user.recruiter)
    search.title = request.form.get('title')
    search.snippet = request.form.get('description')
    search.industry_id = request.form.get('industry')
    l_specific = False if request.form.get('remote') == 'true' else True
    city = request.form.get('city')
    search.public = True if request.form.get('public') == 'true' else False
    if l_specific:
        data = check_location(city.split(',')[0])  # check their entered data
        if data == {}:
            return {'status': 'error', 'message':'An error has occured relating to your location input. Please try again.'}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'error', 'message':'An error has occured relating to your location input. Please try again.'}
        user_codes = add_locations(3, data)
        search.city_id = int(user_codes['city'])
    else:
        search.city_id = None
    db.session.commit()
    return {'status': 'success', 'id': str(search.id)}

@bp.route('/img_upload', methods=['POST'])
@login_required
@restricted_recruiter_admin
def img_upload():
    partner = current_user.recruiter.agency
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return {'status': 'failed',
                    'message': 'We were unable to upload your image. Please try again or select a different image.'}
        else:
            path = 'app/static/uploads/' + file.filename
            os.makedirs('app/static/uploads/', exist_ok=True)
            file.save(path)
            if partner.directory is None or partner.directory == '':
                partner.directory = str(md5(str(partner.id).encode('utf-8')).hexdigest())
            resize_images(path, 'recruiter', partner.recruiters.all()[0].user)
            partner.status = 3
            db.session.add(partner)
            db.session.commit()
            flash("If your image does not appear to change, please try clearing your browser's cache")
            return {'status': 'success'}


@bp.route('/post_new_job_external', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def post_new_job_external():
    lister_id = current_user.recruiter.agency.job_listing_profile.id
    title = str(request.form.get('title'))
    company = str(request.form.get('company'))
    link = str(request.form.get('link'))
    city = str(request.form.get('city'))
    industries = request.form.getlist('industries[]')
    l_specific = True if str(request.form.get('remote')) == 'true' else False
    if not l_specific:
        data = check_location(city.split(',')[0])  # check their entered data
        if data == {}:
            return {'status': 'error',
                    'message': 'An error has occured relating to your location input. Please try again.'}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'error',
                    'message': 'An error has occured relating to your location input. Please try again.'}
        user_codes = add_locations(3, data)
        city_id = int(user_codes['city'])
    else:
        city_id = None
    description = str(request.form.get('description'))
    j = JobListing(location=city, city_id=city_id, date=datetime.utcnow(), company=company, job_title=title, snippet=description,
                   apply_url=link, source=lister_id)
    for i in industries:
        j.industries.append(Industry.query.filter_by(id=int(i)).first_or_404())
    db.session.add(j)
    db.session.commit()
    j.add_recruiter(current_user.recruiter, 0)
    for i in j.recruiters:
        send_email_new_job_posting(i.recruiter, j)
    return {'status':'success', 'id': str(j.id)}


@bp.route('/post_quick_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def post_quick_job():
    lister_id = current_user.recruiter.agency.job_listing_profile.id
    title = str(request.form.get('title'))
    company = str(request.form.get('company'))
    employment = int(request.form.get('employment'))
    low = float(request.form.get('low'))
    high = float(request.form.get('high'))
    compensation = int(request.form.get('compensation'))
    pitch = str(request.form.get('pitch'))
    city = str(request.form.get('city'))
    industries = request.form.getlist('industries[]')
    l_specific = True if str(request.form.get('remote')) == 'true' else False
    if not l_specific:
        data = check_location(city.split(',')[0])  # check their entered data
        if data == {}:
            return {'status': 'error',
                    'message': 'An error has occurred relating to your location input. Please try again.'}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'error',
                    'message': 'An error has occurred relating to your location input. Please try again.'}
        user_codes = add_locations(3, data)
        city_id = int(user_codes['city'])
    else:
        city_id = None
    description = str(request.form.get('description'))
    j = JobListing(location=city, city_id=city_id, date=datetime.utcnow(), company=company, job_title=title, snippet=description,
                   source=lister_id)
    for i in industries:
        j.industries.append(Industry.query.filter_by(id=int(i)).first_or_404())
    db.session.add(j)
    db.session.commit()
    p = QuickApplyProfile(job_id=j.id, employment_type_id=employment, compensation_type_id=compensation, compensation_high=high,
                          compensation_low=low, pitch=pitch)
    db.session.add(p)
    db.session.commit()
    j.add_recruiter(current_user.recruiter, 0)
    for i in j.recruiters:
        send_email_new_job_posting_quick(i.recruiter, j)
    return {'status':'success', 'id': str(j.id)}


@bp.route('/edit_quick_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_quick_job():
    job = JobListing.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        return abort(403)
    job.update_recruiter_association(current_user.recruiter)
    job.job_title = str(request.form.get('title'))
    job.company = str(request.form.get('company'))
    job.quick_apply.employment_type_id = int(request.form.get('employment'))
    job.quick_apply.compensation_low = float(request.form.get('low'))
    job.quick_apply.compensation_high = float(request.form.get('high'))
    job.quick_apply.compensation_type_id = int(request.form.get('compensation'))
    job.quick_apply.pitch = str(request.form.get('pitch'))
    city = str(request.form.get('city'))
    industries = request.form.getlist('industries[]')
    l_specific = True if str(request.form.get('remote')) == 'true' else False
    if not l_specific:
        data = check_location(city.split(',')[0])  # check their entered data
        if data == {}:
            return {'status': 'error',
                    'message': 'An error has occurred relating to your location input. Please try again.'}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'error',
                    'message': 'An error has occurred relating to your location input. Please try again.'}
        user_codes = add_locations(3, data)
        city_id = int(user_codes['city'])
        location = city
    else:
        city_id = None
        location = None
    job.city_id = city_id
    job.location = location
    job.snippet = str(request.form.get('description'))
    for i in industries:
        if i not in job.industries:
            job.industries.append(Industry.query.filter_by(id=int(i)).first_or_404())
    db.session.commit()
    return {'status':'success', 'id': str(job.id)}



@bp.route('/edit_job_external', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_job_external():
    job = JobListing.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        return abort(403)
    job.update_recruiter_association(current_user.recruiter)
    job.job_title = str(request.form.get('title'))
    job.company = str(request.form.get('company'))
    job.apply_url = str(request.form.get('link'))
    job.description = str(request.form.get('description'))
    industries = request.form.getlist('industries[]')
    for i in industries:
        if i not in job.industries:
            job.industries.append(Industry.query.filter_by(id=int(i)).first_or_404())
    city = str(request.form.get('city'))

    l_specific = False if str(request.form.get('remote')) == 'true' else True
    if not l_specific:
        data = check_location(city.split(',')[0])  # check their entered data
        if data == {}:
            return {'status': 'error',
                    'message': 'An error has occured relating to your location input. Please try again.'}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'error',
                    'message': 'An error has occured relating to your location input. Please try again.'}
        user_codes = add_locations(3, data)
        city_id = int(user_codes['city'])
    else:
        city_id = None
        city = None
    job.city_id = city_id
    job.location = city

    db.session.commit()
    return {'status':'success', 'id': str(job.id)}


@bp.route('/delete_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def delete_job():
    j = JobListing.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not j.active:
        if not j.has_recruiter(current_user.recruiter):
            return abort(403)
        for i in j.recruiters:
            send_email_job_deleted(i.recruiter, j)
        j.delete_posting()
        return {'status': 'success'}
    else:
        return abort(404)


@bp.route('/deactivate_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def deactivate_job():
    j = JobListing.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not j.has_recruiter(current_user.recruiter):
        return abort(403)
    if not j.active:
        return abort(404)
    for i in j.recruiters:
        send_email_job_deactivated(i.recruiter, j)
    if j.quick_apply != None:
        for x in j.quick_apply.applicants:
            if x.user.recruiter_visibility == 3:
                send_email_job_no_longer_available(j, x.user)
    j.update_recruiter_association(current_user.recruiter)
    j.deactivate()
    return {'status': 'success', 'url': '/user/' + str(current_user.username)}


@bp.route('/reactivate_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def reactivate_job():
    j = JobListing.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not j.has_recruiter(current_user.recruiter):
        return abort(403)
    if j.active:
        return abort(404)
    for i in j.recruiters:
        send_email_job_reactivated(i.recruiter, j)
    if j.quick_apply != None:
        for x in j.quick_apply.applicants:
            if x.user.recruiter_visibility == 3:
                send_email_job_available_again(j, x.user)
    j.update_recruiter_association(current_user.recruiter)
    j.activate()
    return {'status': 'success'}


@bp.route('/delete_talent_search', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def delete_talent_search():
    j = SavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if j.status == 0:
        if not j.has_recruiter(current_user.recruiter):
            return abort(403)
        for i in j.recruiters:
            send_email_search_deleted(i.recruiter, j)
        j.delete()
        return {'status': 'success'}
    else:
        return abort(404)


@bp.route('/deactivate_talent_search', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def deactivate_talent_search():
    j = SavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not j.has_recruiter(current_user.recruiter):
        return abort(403)
    if not j.status == 1:
        return abort(404)
    for i in j.recruiters:
        send_email_search_deactivated(i.recruiter, j)
    j.update_recruiter_association(current_user.recruiter)
    j.terminate()
    return {'status': 'success', 'url': '/user/' + str(current_user.username)}


@bp.route('/reactivate_talent_search', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def reactivate_talent_search():
    j = SavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not j.has_recruiter(current_user.recruiter):
        return abort(403)
    if not j.status == 0:
        return abort(404)
    for i in j.recruiters:
        send_email_search_reactivated(i.recruiter, j)
    j.update_recruiter_association(current_user.recruiter)
    j.reactivate()
    return {'status': 'success'}


@bp.route('/save_candidate_orders', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def save_candidate_orders():
    search = SavedSearch.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not search.has_recruiter(current_user.recruiter):
        return abort(403)
    orders = request.form.getlist('orders[]')
    search.reorders(orders)
    search.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/save_applicant_orders', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def save_applicant_orders():
    job = JobListing.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        return abort(403)
    orders = request.form.getlist('orders[]')
    job.quick_apply.reorders(orders)
    job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}

@bp.route('/remove_candidate', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def remove_candidate():
    c = Candidate.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if c.status < 0:
        return abort(404)
    if not c.search.has_recruiter(current_user.recruiter):
        return abort(403)
    c.search.remove_candidate(c.id)
    c.search.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/re_init_candidate', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def re_init_candidate():
    c = Candidate.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if c.status > 0:
        return abort(404)
    if not c.search.has_recruiter(current_user.recruiter):
        return abort(403)
    c.search.reinitiate_candidate(c.id)
    c.search.update_recruiter_association(current_user.recruiter)

    return {'status': 'success'}

@bp.route('/remove_applicant', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def remove_applicant():
    a = Applicant.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if a.status < 0:
        return abort(404)
    if not a.application.job.has_recruiter(current_user.recruiter):
        return abort(403)
    a.application.remove_applicant(a.id)
    a.application.job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/re_init_applicant', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def re_init_applicant():
    a = Applicant.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if a.status > 0:
        return abort(404)
    if not a.application.job.has_recruiter(current_user.recruiter):
        return abort(403)
    a.application.reinitiate_applicant(a.id)
    a.application.job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/get_search_info', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def get_search_info():
    s = SavedSearch.query.filter_by(id=int(request.args.get('a'))).first_or_404()
    if not s.has_recruiter(current_user.recruiter):
        abort(403)
    json = {}
    json['status'] = 'success'
    json['title'] = s.title
    json['description'] = s.snippet
    json['industry'] = s.industry_id
    json['public'] = 1 if s.public else 0
    json['l_specific'] = 1 if s.l_specific else 0
    if s.l_specific:
        json['city'] = s.city.name
    else:
        json['city'] = ''
    json['removed'] = s.get_removed_candidates_html()
    s.update_recruiter_association(current_user.recruiter)

    return json


@bp.route('/get_removed_applicants', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def get_removed_applicants():
    a = JobListing.query.filter_by(id=int(request.args.get('a'))).first_or_404()
    if not a.has_recruiter(current_user.recruiter):
        abort(403)
    json = {}
    json['status'] = 'success'
    json['removed'] = a.quick_apply.get_removed_applicants_html()
    a.update_recruiter_association(current_user.recruiter)
    return json


@bp.route('/edit_ss_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_ss_note():
    note = SavedSearchNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    note.search.update_recruiter_association(current_user.recruiter)

    return {'status': 'success'}


@bp.route('/edit_candidate_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_candidate_note():
    note = CandidateNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    note.candidate.search.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/del_ss_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def del_ss_note():
    note = SavedSearchNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    note.search.update_recruiter_association(current_user.recruiter)

    return {'status': 'success'}


@bp.route('/del_candidate_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def del_candidate_note():
    note = CandidateNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    # note.candidate.search.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/edit_job_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_job_note():
    note = JobPostingNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    # note.job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/edit_applicant_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def edit_applicant_note():
    note = ApplicantNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    # note.applicant.application.job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/del_applicant_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def del_applicant_note():
    note = ApplicantNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    print('hi')
    # note.applicant.application.job.update_recruiter_association(current_user.recruiter)

    return {'status': 'success'}


@bp.route('/del_job_note', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def del_job_note():
    note = JobPostingNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    # note.job.update_recruiter_association(current_user.recruiter)
    return {'status': 'success'}


@bp.route('/get_applicant_info', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def get_applicant_info():
    a = Applicant.query.filter_by(id=int(request.args.get('a'))).first_or_404()
    if not a.application.job.has_recruiter(current_user.recruiter):
        abort(403)
    html = a.render_html()
    a.clear_notifications(current_user)
    a.application.job.update_recruiter_association(current_user.recruiter)

    return {'status': 'success', 'html': html}

@bp.route('/get_candidate_info', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def get_candidate_info():
    a = Candidate.query.filter_by(id=int(request.args.get('a'))).first_or_404()
    if not a.search.has_recruiter(current_user.recruiter):
        abort(403)
    html = a.render_html()
    a.clear_notifications(current_user)
    a.search.update_recruiter_association(current_user.recruiter)

    return {'status': 'success', 'html': html}


@bp.route('/load_more_candidates', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def load_more_candidates():
    start = (int(request.args.get('set')) * 5)
    search = SavedSearch.query.filter_by(id=int(request.args.get('search_id'))).first_or_404()
    if not search.has_recruiter(current_user.recruiter):
        return abort(403)
    search.update_recruiter_association(current_user.recruiter)
    candidates = search.get_candidates(type=int(request.args.get('order')), start=start, user=current_user)
    html = ''
    if len(candidates) > 0:
        for candidate in candidates:
            html += candidate.render_html_card()
    else:
        html += "<div class='row' id='no-more-candidates'><div class='col-sm-12 no-more-indicator'>That's all of the candidates right now </div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/load_more_applicants', methods=['GET'])
@login_required
@restricted_recruiter
@restricted_completed
def load_more_applicants():
    start = (int(request.args.get('set')) * 5)
    job = JobListing.query.filter_by(id=int(request.args.get('job_id'))).first_or_404()
    if not job.has_recruiter(current_user.recruiter):
        return abort(403)
    job.update_recruiter_association(current_user.recruiter)
    applicants = job.quick_apply.get_applicants(type=int(request.args.get('order')), start=start, user=current_user)
    html = ''
    if len(applicants) > 0:
        for applicant in applicants:
            html += applicant.render_html_card()
    else:
        html += "<div class='row' id='no-more-applicants'><div class='col-sm-12 no-more-indicator'>That's all of the applicants right now </div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/share_recruiter', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def share_recruiter():
    s_id, r_id = int(request.form.get('search_id')), int(request.form.get('recruiter_id'))
    s = SavedSearch.query.filter_by(id=s_id).first_or_404()
    if not s.has_recruiter(current_user.recruiter):
        abort(403)
    if s.get_recruiter_association(current_user.recruiter).level != 0:
        abort(403)
    r = Recruiter.query.filter_by(id=int(r_id), agency_id=int(s.agency_id), status=1).first_or_404()
    a = s.add_recruiter(r)
    if a is not None:
        send_email_shared_search(r.user, current_user, s)
        html = a.render_html()
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed'}


@bp.route('/share_recruiter_job', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def share_recruiter_job():
    s_id, r_id = int(request.form.get('job_id')), int(request.form.get('recruiter_id'))
    s = JobListing.query.filter_by(id=s_id).first_or_404()
    if not s.has_recruiter(current_user.recruiter):
        abort(403)
    if s.get_recruiter_association(current_user.recruiter).level != 0:
        abort(403)
    r = Recruiter.query.filter_by(id=int(r_id), agency_id=int(s.lister.agency_id), status=1).first_or_404()
    a = s.add_recruiter(r, 3)
    if a is not None:
        send_email_shared_job(r.user, current_user, s)
        html = a.render_html()
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed'}

@bp.route('/update_message_activity_applicant', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def update_message_activity_applicant():
    applicant = Applicant.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not applicant.application.job.has_recruiter(current_user.recruiter):
        abort(403)
    board = applicant.message_board.first_or_404()
    if current_user not in board.members:
        abort(403)
    applicant.application.job.update_recruiter_association(current_user.recruiter)
    applicant.clear_notifications(current_user)
    activity = board.activity.filter_by(user_id=current_user.id).first_or_404()
    activity.last_seen = RecruiterJobAssociation.query.filter_by(job_id=applicant.application.job_id,
                                                                    recruiter_id=current_user.recruiter.id).first_or_404().last_active
    board.clear_notifications(current_user)
    db.session.commit()

    return {'status': 'success'}

@bp.route('/send_applicant_message', methods=['POST'])
@login_required
@restricted_recruiter
@restricted_completed
def send_applicant_message():
    applicant = Applicant.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not applicant.application.job.has_recruiter(current_user.recruiter):
        return {'status': 'failed', 'message':'You are not allowed to edit this search'}
    applicant.application.job.update_recruiter_association(current_user.recruiter)
    applicant.clear_notifications(current_user)
    if applicant.message_board.first() is None:
        # create board for candidate, add participants, and send message
        subject = "'" + str(applicant.application.job.job_title) + "' ~~ " + str(applicant.user.name)
        board = MessageBoard(subject=subject, last_active=datetime.utcnow(), recruiting=True,
                         applicant_id=applicant.id)  # create board
        db.session.add(board)
        db.session.commit()
        for r in applicant.application.job.recruiters:
            board.add_member(r.recruiter.user)
        board.add_member(applicant.user)
        board.send_message(current_user, message=str(request.form.get('q')))
        return {'status': 'success'}
    else:
        board = applicant.message_board.first()
        board.send_message(current_user, message=str(request.form.get('q')))
    html = ''
    for i in board.get_messages(0, 0)[::-1]:
        html += i.render_html()
    return {'status': 'success', 'html': html}