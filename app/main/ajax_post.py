from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import User, Forum, Post, Comment, CommentVote, Message, MessageBoard, City, Industry, JobListing, \
    JobListingActivity, MessageBoardActivity, Candidate, \
    JobFound, SuggestedForum, JobSavedSearch, JobSSNote, JobListingNote, Employer, Institution, \
    EmployerAssociations, RecruitingProfile, Notification, CommentReport, PostReport, Country, \
    Value, Skill, Background, Hobby, Interest, MessageBoardAssociations, BlogPost, ExclusivePartner, PartnerClicks, \
    Event, Appointment, AppointmentParticipantAssociations, MentorNote, NewsArticle, MentorProfile

from app.background.emails import *
from datetime import datetime, timedelta
from boto3 import resource, client
import os
import json
from indeed import IndeedClient
from app.auth.emails import send_email_edit_profile_changes, send_email_account_deletion_confirmed, send_email_account_deletion_request
from app.main.emails import send_email_recruiting_unenroll, send_email_new_testimonial
from app.tasks import check_location, add_locations, upload_file, resize_images
from app.main.tasks import extract_resume_data, add_employer, add_institution
from app.auth.tasks import check_entered_location
from app.general import restricted_user, restricted_completed
from app.main.emails import *
from app.auth.emails import *
from app.partnership.emails import send_email_new_applicant, send_email_applicant_removed
from hashlib import md5


@bp.route('/vote_comment/<id>/<option>', methods=['POST'])
@login_required
@restricted_user
def vote_comment(id, option):
    comment = Comment.query.get(id)
    if comment is not None:
        if CommentVote.query.filter_by(user_id=current_user.id, comment_id=comment.id).count() > 0:
            vote = CommentVote.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()
            if option == '1':
                if vote.direction == 0:
                    vote.direction = 1
                    db.session.add(vote)
                else:
                    db.session.delete(vote)
            elif option == '0':
                if vote.direction == 1:
                    vote.direction = 0
                    db.session.add(vote)
                else:
                    db.session.delete(vote)
        else:
            if option == '1':
                vote = CommentVote(user_id=current_user.id, comment_id=comment.id, direction=1)
            elif option == '0':
                vote = CommentVote(user_id=current_user.id, comment_id=comment.id, direction=0)
            db.session.add(vote)
        db.session.commit()
    return {'status':'success', 'url': request.referrer}


@bp.route('/delete_profile_images', methods=['GET'])
@login_required
def delete_profile_images():
    if not current_user.img:
        abort(403)
    s3 = client('s3', region_name='us-east-1',
                aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                aws_secret_access_key='current_app.config.get('AWS_SECRET')')
    s3_resource = resource('s3', region_name='us-east-1',
                           aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                           aws_secret_access_key='current_app.config.get('AWS_SECRET')')

    bucket = s3_resource.Bucket('ilmjtcv-user-static-files')
    for file in bucket.objects.filter(Prefix=current_user.directory):
        if 'user_img' in file.key:
            s3.delete_object(Bucket='ilmjtcv-user-static-files', Key=file.key)
    current_user.img = False
    db.session.add(current_user)
    db.session.commit()
    send_email_edit_profile_changes(current_user, [{'field': 'user image',
                                                    'old': '(previously uploaded)',
                                                    'new': 'None'}])
    flash("If your image does not appear to change, please try clearing your browser's cache")
    return {'status': 'success', 'message': 'The user image that you uploaded previously has been deleted.'}

#
# @bp.route('/delete_post/<type>/<id>')
# @login_required
# @restricted_user
# def delete_post(type, id):
#     if type == '0':
#         post = Post.query.filter_by(id=id).first_or_404()
#         if post.author != current_user:
#             flash('You may only delete posts that you have authored.')
#             return redirect(url_for('main.post', id=id))
#         post.deleted = 1
#         post.date_deleted = datetime.utcnow()
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been deleted')
#         return redirect(url_for('main.forum', id=post.forum_id))
#     elif type == '1':
#         comment = Comment.query.filter_by(id=id).first_or_404()
#         if comment.author != current_user:
#             flash('You may only delete comments that you have authored.')
#             return redirect(url_for('main.post', id=comment.post_id))
#         comment.deleted = 1
#         comment.date_deleted = datetime.utcnow()
#         db.session.add(comment)
#         db.session.commit()
#         flash('Your comment has been deleted')
#         return redirect(url_for('main.post', id=comment.post.id))
#     else:
#         flash('Invalid Request')
#         return redirect(url_for('main.chat'))


@bp.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    search = request.args.get('q')
    users = User.query.filter(User.username.like('%' + str(search) + '%')).all()
    results = [x.username for x in users if not x.is_recruiter]
    return jsonify(matching_results=results)


@bp.route('/add_job_search', methods=['POST'])
def add_job_search():
    # print(request.form)
    if request.form.get('l') == 'true':
        # print(request.form.get('c'))
        data = check_location(str(request.form.get('c')))  # check their entered data
        # print(data)
        if data == {}:
            return {'status': 'failed',
                    'message': "'An error occurred related to your location... please try again. If there error persists please let us know at support@ilmjtcv.com'"}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'failed',
                    'message': "'An error occurred related to your location... please try again. If there error persists please let us know at support@ilmjtcv.com'"}
        user_codes = add_locations(3, data)
        # print(user_codes)
        cityid = user_codes['city']
        search = JobSavedSearch(title=str(request.form.get('t')), snippet=str(request.form.get('d')),
                                user_id=current_user.id,
                                l_specific=True,
                                city_id=cityid, proximity_id=str(request.form.get('p')), status=1,
                                start=datetime.utcnow(),
                                last_updated=datetime.utcnow(), last_checked=datetime.utcnow() - timedelta(minutes=5))
    else:
        search = JobSavedSearch(title=str(request.form.get('t')), snippet=str(request.form.get('d')),
                                user_id=current_user.id,
                                l_specific=False, proximity_id=str(request.form.get('p')), status=1,
                                start=datetime.utcnow(),
                                last_updated=datetime.utcnow(), city_id=None,
                                last_checked=datetime.utcnow() - timedelta(minutes=5))
    industries = [int(i) for i in request.form.getlist('industries[]')]
    for i in industries:
        search.industries.append(Industry.query.filter_by(id=int(i)).first_or_404())
    db.session.add(search)
    db.session.commit()
    search.get_first_page_results()
    current_user.suggest_forums(new_search=True)
    return {'status': 'success', 'id': str(search.id)}

@bp.route('/edit_job_search', methods=['POST'])
def edit_job_search():
    s = JobSavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if s.user != current_user:
        abort(403)
    if request.form.get('l') == 'true':
        data = check_location(str(request.form.get('c')))  # check their entered data
        if data == {}:
            return {'status': 'failed',
                    'message': "'An error occurred related to your location... please try again. If there error persists please let us know at support@ilmjtcv.com'"}
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return {'status': 'failed',
                    'message': "'An error occurred related to your location... please try again. If there error persists please let us know at support@ilmjtcv.com'"}
        user_codes = add_locations(3, data)
        cityid = user_codes['city']
        l_s = True
    else:
        cityid = None
        l_s = False
    new_location = False
    s.title = str(request.form.get('t'))
    s.snippet = str(request.form.get('d'))
    if s.l_specific != l_s:
        new_location = True
        s.l_specific = l_s
    s.proximity_id = str(request.form.get('p'))
    s.last_updated = datetime.utcnow()
    if s.city_id != cityid:
        new_location = True
        s.city_id = cityid
    s.last_checked = datetime.utcnow() - timedelta(minutes=5)
    db.session.commit()
    if new_location:
        s.get_first_page_results()
    current_user.suggest_forums(new_search=True)
    return {'status': 'success', 'id': str(s.id)}


@bp.route('/data/mapbox_geojson', methods=['GET'])
def geojson():
    s3 = resource('s3', region_name='us-east-1',
                           aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                           aws_secret_access_key='current_app.config.get('AWS_SECRET')')
    obj = s3.Object('ilmjtcv-geojson', 'geojson.json')
    body = json.loads(obj.get()['Body'].read().decode('utf-8'))
    return jsonify(body)


@bp.route('/edit_job_activity', methods=['POST'])
@login_required
def edit_job_activity():
    job = JobListingActivity.query.filter_by(id=int(request.form.get('id')))
    if job.count() == 0:
        return {'status': 'failed'}
    else:
        activity = job.first()
        if activity.search.user != current_user:
            return {'status': 'failed'}
    if int(request.form.get('option')) == -1 or int(request.form.get('option')) == 2:
        direction = int(request.form.get('option'))
    else:
        direction = 0
    if JobListingActivity.query.filter_by(search_id=activity.search_id, status=int(direction)).count() > 0:
        last_order = JobListingActivity.query.filter_by(search_id=activity.search_id, status=int(direction)).order_by(JobListingActivity.order.desc()).first().order
        if last_order is None:
            last_order = 0
    else:
        for o in JobListingActivity.query.filter_by(search_id=activity.search_id, status=int(activity.status)).all():
            if o.order is not None and o.order> activity.order:
                o.order -= 1
        last_order = 0
    activity.order = last_order + 1
    activity.status = int(direction)
    db.session.commit()
    return {'status': 'success'}



@bp.route('/open_job_application/<id>')
@restricted_user
@restricted_completed
def open_job_application(id):
    j = JobListingActivity.query.filter_by(id=int(id))
    if j.count() == 0:
        flash('An error has occurred. Please try again')
        return redirect(url_for('main.job_search', id=j.first().search_id))
    else:
        if j.first().search.user != current_user:
            flash('You are only allowed to edit your own job searches!')
            return redirect(url_for('main.job_search', id=j.search_id))
        activity = JobListingActivity.query.filter_by(id=int(id)).first()
    if activity.status == 0:
        ordering = JobListingActivity.query.filter_by(search_id=j.first().search.id, status=1)
        if ordering.count() > 0:
            last_order = ordering.order_by(JobListingActivity.order.desc()).first().order
        else:
            last_order = 0
        activity.order = last_order + 1
        activity.status = 1
    db.session.commit()
    if j.first().job.apply_url is not None and j.first().job.apply_url != '':
        return redirect(j.first().job.apply_url)
    else:
        return redirect(j.first().job.indeed_url)


@bp.route('/send_recruiter_message', methods=['POST'])
@login_required
def send_recruiter_message():
    candidate = Candidate.query.filter_by(id=int(request.form.get('c'))).first_or_404()
    if candidate.search.public:
        if MessageBoard.query.filter_by(recruiting=True, candidate_id=candidate.id).count() == 0:
            m = MessageBoard(subject=str(request.form.get('s')), last_active=datetime.utcnow(), recruiting=True, candidate_id=candidate.id)  # create board
            db.session.add(m)
            db.session.commit()
            for r in candidate.search.recruiters:
                m.add_member(r.recruiter.user)
            m.add_member(candidate.user)
            m.send_message(current_user, str(request.form.get('m')))
            return {'status': 'success'}
        else:
            abort(404)
    else:
        abort(403)


@bp.route('/submit_job_found', methods=['POST'])
@login_required
def submit_job_found():
    message = request.form.get('m')
    testimonial = request.form.get('t')
    if testimonial == 'true':
        t = True
    else:
        t = False
    j = JobFound(user_id=current_user.id, testimonial=t, message=message, timestamp=datetime.utcnow())
    db.session.add(j)
    db.session.commit()
    send_email_new_testimonial(j)
    return 'HELLLOOOO'


@bp.route('/post_job_search_note', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def post_job_search_note():
    search = JobSavedSearch.query.filter_by(id=int(request.form.get('search_id'))).first_or_404()
    if search.user != current_user:
        flash('You are only allowed to view your own job searches!')
        return redirect(url_for('main.jobs'))
    j = JobSSNote(body=str(request.form.get('q')), search_id=search.id, timestamp=datetime.utcnow())
    db.session.add(j)
    db.session.commit()
    html = j.render_html()
    return {'status':'success', 'html': html}


@bp.route('/post_job_note', methods=['POST'])
@login_required
def post_job_note():
    job = JobListingActivity.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if job.search.user != current_user:
        return {'status':'failed', 'message':'You are only allowed to view your own job searches!'}
    j = JobListingNote(body=str(request.form.get('q')), job_id=job.job_id,
                       timestamp=datetime.utcnow(), search_id=job.search_id)
    db.session.add(j)
    db.session.commit()
    html = j.render_html()
    return {'status':'success', 'html': html}


@bp.route('/terminate_job_search/<id>')
@login_required
@restricted_user
@restricted_completed
def terminate_job_search(id):
    search = JobSavedSearch.query.filter_by(id=int(id)).first_or_404()
    if search.user != current_user:
        flash('You are only allowed to view your own job searches!')
        return redirect(url_for('main.jobs'))
    search.status = 0
    db.session.commit()
    return redirect(url_for('main.jobs'))


@bp.route('/activate_job_search/<id>')
@login_required
@restricted_user
@restricted_completed
def activate_job_search(id):
    search = JobSavedSearch.query.filter_by(id=int(id)).first_or_404()
    if search.user != current_user:
        flash('You are only allowed to view your own job searches!')
        return redirect(url_for('main.jobs'))
    search.status = 1
    db.session.commit()
    return redirect(url_for('main.job_search', id=search.id))


@bp.route('/enroll_resume_upload', methods=['POST', 'GET'])
def enroll_resume_upload():
    if request.method == 'POST':
        if current_user.recruiter_visibility == 3:
            flash('You are already enrolled in recruiter visibility.')
            return redirect(url_for('main.recruiting'))
        if current_user.recruiting_profile is None:
            try:
                resume = request.files.get('resume')
                path = 'app/static/uploads/' + str(current_user.username) + '.pdf'
                os.makedirs('app/static/uploads/', exist_ok=True)
                resume.save(path)
                if current_user.recruiting_profile is None:
                    profile = RecruitingProfile(user_id=current_user.id)
                else:
                    profile = current_user.recruiting_profile
                profile.cities.append(current_user.city)
                profile.industries.append(current_user.industry)
                db.session.add(profile)
                db.session.commit()
                # print('hi')
                # data = extract_resume_data(path, str(current_user.username) + '.pdf')
                # add_resume_data(data)
                filename = upload_file(file=path, user=current_user, bucket='user', extension='application/pdf',
                                       name='resume')
                os.remove(path=path)
                current_user.directory = filename
                current_user.resume = True
                current_user.recruiter_visibility = 1
                db.session.commit()
            except:
                return {'value': 'failed'}
        return {'value': 'success', 'institutions': [{'name': x.name, 'id': str(x.id)} for x in current_user.recruiting_profile.institutions],
                'employers': [{'name': x.employer.name, 'id': str(x.id)} for x in current_user.recruiting_profile.employers]}
    else:
        return{'value': 'success', 'institutions': [{'name': x.name, 'id': str(x.id)} for x in current_user.recruiting_profile.institutions],
                'employers': [{'name': x.employer.name, 'id': str(x.id)} for x in current_user.recruiting_profile.employers]}


@bp.route('/change_job_order/<id>', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def change_job_order(id):
    search = JobSavedSearch.query.filter_by(id=int(id)).first_or_404()
    # print(request.form)
    uninterested = request.form.getlist('q[0][]')
    viewed = request.form.getlist('q[1][]')
    considering = request.form.getlist('q[2][]')
    applied = request.form.getlist('q[3][]')
    categories = [applied, considering, viewed, uninterested]
    # print(categories)
    for c in range(len(categories)):
        if len(categories[c]) > 0 and categories[c][0] != '':
            for i in range(len(categories[c])):
                ca = JobListingActivity.query.filter_by(search_id=search.id, status=int(c),
                                               job_id=int(categories[c][i].split('_')[1])).first()
                ca.order = int(i) + 1
                db.session.add(ca)
                db.session.commit()
    return jsonify('success')


@bp.route('/check_keyword/<search_id>/<keyword>')
@login_required
@restricted_user
@restricted_completed
def check_keyword(search_id, keyword):
    search = JobSavedSearch.query.filter_by(id=int(search_id)).first_or_404()
    client = IndeedClient('current_app.config.get('INDEED_API')')
    total = 0
    for industry in search.industries:
        if search.l_specific:
            initial_params = {
        'q': industry.title + str(keyword),
        'l': search.city.name + ' ' + str(search.city.state.name),
        'userip': "1.2.3.4",
        'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
        'radius': str(search.proximity.title.split(' miles')[0]),
        'limit': '10',
        'co': search.city.country.code,
        'filter': '1',
        'latlong': '1'
    }
        else:
            initial_params = {
                'q': industry.title + str(keyword),
                'userip': "1.2.3.4",
                'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                'radius': str(search.proximity.title.split(' miles')[0]),
                'limit': '10',
                'co': search.city.country.code,
                'filter': '1',
                'latlong': '1'
            }
        results = client.search(**initial_params)
        total += int(results['totalResults'])
    if total < 1:
        return {'Error': 'This is not a widely used keyword in the industries that apply to your search. Please choose another one.'}
    else:
        return {'Success': 'yay'}

@bp.route('/test_emails')
@login_required
def test_emails():
    if current_user.username in ['giladspitzer', 'gmoney', 'abbystein7', 'sstadlan', 'giladrecruiter', 'pablo_f']:
        return render_template('email_testing.html')
    else:
        return abort(403)


@bp.route('/test_email/<num>')
@login_required
def test_email(num):
    if current_user.username in ['giladspitzer', 'giladrecruiter', 'abbystein7', 'sstadlan', 'giladspitzer', 'pablo_f']:
        class Org:
            request_name = ''
            request_email = ''

            def __init__(self, user):
                self.request_name = user.name
                self.request_email = user.email
            def get_initial_confirm_token(self):
                return 'fdsafdsfkdsajfkdsajkfjkdaslfjdaksjiofjd'
        if int(num) == 0:
            org = Org(current_user)
            send_email_partnership_received(org)
        # elif int(num) == 1:
        #     org = Org(current_user)
        #     send_email_partnership_confirm(org)
        elif int(num) == 2:
            send_email_confirm_password_reset(current_user)
        elif int(num) == 3:
            send_email_confirm_registration(current_user)
        elif int(num) == 4:
            send_email_confirm_email(current_user)
        elif int(num) == 5:
            send_password_reset_email(current_user)
        elif int(num) == 6:
            send_email_confirm_new_email(current_user)
        elif int(num) == 7:
            changes = [{'field':'resume', 'old':'previously uploaded', 'new':'newly uploaded'}, {'field':'name', 'old':'Testing', 'new':'Testing123'}, {'field':'Username', 'old':'oldUsername', 'new':'newUsername'}]
            send_email_edit_profile_changes(current_user, changes)
        elif int(num) == 8:
            data = 'testing123fdajkfdslajfkdsjafdask'
            send_user_confirmed_report(data, current_user)
        elif int(num) == 9:
            send_email_recruiting_enroll(current_user)
        elif int(num) == 10:
            send_email_recruiting_unenroll(current_user)
        if int(num) == 11:
            send_email_confirm_recruiter_registration(current_user)
        elif int(num) == 12:
            send_email_never_enrolled_recruiting(current_user)
        # elif int(num) == 12:
        #     send_email_new_jobs(current_user)
        flash('Message Sent')
        return redirect(url_for('main.test_emails'))
    else:
        return abort(403)


@bp.route('/add_institution_recruiting', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def add_institution_recruiting():
    i, l = request.form.get('i'), request.form.get('l')
    try:
        city = str(request.form.get('l')).split(',')[0]
    except:
        city = str(request.form.get('l'))
    data = {'name': i, 'city': city}
    id = add_institution(data)
    if id != 0:
        return {'status': 'success', 'id': id}
    else:
        return {'status': 'failed', 'id': id, 'message': 'Please enter a valid city'}


@bp.route('/add_employer_recruiting', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def add_employer_recruiting():
    name = request.form.get('name')
    try:
        start = datetime.strftime(datetime.strptime(request.form.get('start'), '%m/%d/%Y'), '%m/%d/%Y')
    except:
        start = datetime.strftime(datetime.utcnow(), '%m/%d/%Y')
    current = request.form.get('is_current')
    description = request.form.get('description')
    if current == 'true':
        is_current = 'true'
        end = ''
    else:
        is_current = 'false'
        end = datetime.strftime(datetime.strptime(request.form.get('end'), '%m/%d/%Y'), '%m/%d/%Y')
    employer_name = Employer.query.filter_by(name=name)
    if employer_name.count() == 0:
        id = add_employer({'employer': name, 'description': description, 'is_current': is_current, 'start': start, 'end': end})
    else:
        employer_associations = EmployerAssociations.query.filter_by(profile_id=current_user.recruiting_profile.id, employer_id=employer_name.first().id)
        if employer_associations.count() == 0:
            id = add_employer(
                {'employer': name, 'description': description, 'is_current': is_current, 'start': start, 'end': end})
        else:
            employer_associations.first().update({'description': description, 'is_current': is_current, 'start': start, 'end': end})
            id = employer_associations.first().id
    if id != 0:
        return {'status': 'success', 'id': id}
    else:
        return {'status': 'failed', 'id': id}


@bp.route('/remove_institution', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def remove_institution():
    i_id = request.form.get('id')
    # print(i_id)
    i = Institution.query.filter_by(id=int(i_id)).first_or_404()
    # print(i.users)
    # print(current_user.recruiting_profile)
    if current_user.recruiting_profile in i.users:
        i.users.remove(current_user.recruiting_profile)
    db.session.commit()
    return 'JHELLO'


@bp.route('/remove_employer', methods=['POST', 'GET'])
@login_required
@restricted_user
@restricted_completed
def remove_employer():
    id = request.form.get('id')
    a = EmployerAssociations.query.filter_by(id=int(id), profile_id=current_user.recruiting_profile.id).first_or_404()
    db.session.delete(a)
    db.session.commit()
    return 'JHELLO'


@bp.route('/recruiting_step_change/<num>', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def recruiting_step_change(num):
    if current_user.recruiter_visibility != int(num) - 1:
        return {'status': 'failed'}
    else:
        current_user.recruiter_visibility = int(num)
        db.session.commit()
        return {'status': 'success'}


@bp.route('/complete_recruiting_registration', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def complete_recruiting_registration():
    profile = current_user.recruiting_profile
    cities = request.form.getlist('cities[]')
    additional = request.form.get('additional')
    industries = request.form.getlist('industries[]')
    profile.experience_id = int(request.form.get('experience'))
    profile.additional_bio = additional
    # add industries
    profile.industries.clear()
    for industry in industries:
        i = Industry.query.filter_by(id=int(industry)).first_or_404()
        profile.industries.append(i)

    # add cities if applicable
    if request.form.get('l_specific') == 'true':
        profile.remote = False
        profile.cities.clear()
        for city in cities:
            try:
                c = str(city).split(',')[0]
            except:
                c = city
            city_name = City.query.filter_by(name=c)
            if city_name.count() == 0:
                data = check_location(str(c))
                if 'city' not in list(data.keys()):  # if no postal code then return redirect
                    return {'status': 'failed', 'message': 'An error occurred related to your location... please try again. If there error persists '
                  'please let us know at support@ilmjtcv.com'}
                user_codes = add_locations(3, data)
                city_id = user_codes['city']
                city_id = City.query.filter_by(id=city_id).first()
            else:
                city_id = city_name.first()
            profile.cities.append(city_id)
    else:
        profile.remote = True

    # add date laid off if applicable
    if request.form.get('laid_off') != '':
        profile.date_laid_off = datetime.strptime(request.form.get('laid_off'), '%m/%d/%Y')
    if current_user.recruiter_visibility != 3:
        send_email_recruiting_enroll(current_user)
    current_user.recruiter_visibility = 3
    db.session.commit()
    return {'status': 'success'}


@bp.route('/recruiting_more_info', methods=['GET'])
@login_required
@restricted_user
@restricted_completed
def recruiting_more_info():
    profile = current_user.recruiting_profile
    # print(profile.remote)
    if profile.date_laid_off is None:
        laid_off = ''
    else:
        laid_off = datetime.strftime(profile.date_laid_off, '%m/%d/%Y')
    if not profile.remote:
        cities = [x.name for x in profile.cities]
    else:
        cities = []
    industries = [x.id for x in profile.industries]
    l_specific = 'false' if profile.remote else 'true'
    data = {'bio':profile.additional_bio, 'laid_off': laid_off, 'experience':profile.experience_id,
            'l_specific':l_specific, 'cities': cities, 'industries': industries}
    return data


# @bp.route('/join_forum/<id>', methods=['POST'])
# @login_required
# @restricted_user
# def join_forum(id):
#     forum = SuggestedForum.query.filter_by(id=int(id)).first_or_404()
#     forum.status = 2
#     forum.forum.users.append(current_user)
#     db.session.commit()
#     return redirect(url_for('main.chat', id=forum.forum_id))


# @bp.route('/leave_forum/<fid>', methods=['POST'])
# @login_required
# @restricted_user
# def leave_forum(fid):
#     print(fid)
#     forum = Forum.query.filter_by(id=int(fid)).first_or_404()
#     if forum.location_type != -1:
#         forum.users.remove(current_user)
#         suggestion = SuggestedForum.query.filter_by(forum_id=forum.id, user_id=current_user.id).first_or_404()
#         suggestion.status = 1
#         db.session.commit()
#     return redirect(url_for('main.chat'))


@bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    board = MessageBoard.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if current_user not in board.members:
        return {'status': 'failed', 'message': 'You do not have access to that thread'}
    board.send_message(current_user, str(request.form.get('q')))
    messages = board.get_messages(type=0, start=0)
    html = ''
    if len(messages) > 0:
        for message in messages[::-1]:
            html += message.render_html()
    else:
        html += "<div class='row' id='no-more-messages'><div class='col-sm-12 no-more-indicator'></div></div>"
    boards_html = ''
    boards = current_user.get_boards(0, 0)
    for b in boards:
        if b == board:
            boards_html += b.render_html(current=True)
        else:
            boards_html += b.render_html(current=False)
    return {'status': 'success', 'html': html, 'html_boards': boards_html}

@bp.route('/read_notification/<id>', methods=['GET', 'POST'])
@login_required
def read_notification(id):
    n = Notification.query.filter_by(id=int(id)).first_or_404()
    if n.user_id != current_user.id:
        return {'status': 'failed'}
    n.mark_read()
    return {'status': 'success'}

@bp.route('/notification_count', methods=['GET', 'POST'])
@login_required
def notification_count():
    try:
        return {'status': 'success', 'number': str(current_user.new_notifications())}
    except:
        return {'status': 'failed'}


@bp.route('/like_post', methods=['POST'])
@login_required
@restricted_user
def like_post():
    post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
    post.like(current_user)
    return {'status': 'success'}


@bp.route('/unlike_post', methods=['POST'])
@login_required
@restricted_user
def unlike_post():
    post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
    post.unlike(current_user)
    return {'status': 'success'}


@bp.route('/delete_post', methods=['POST'])
@login_required
@restricted_user
def delete_post():
    post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
    # print(post)
    if post.author == current_user:
        post.delete()
        return {'status': 'success'}
    else:
        abort(403)

@bp.route('/flag_post', methods=['POST'])
@login_required
@restricted_user
def flag_post():
    if int(request.form.get('report_type')) == 0:
        post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
        if post.author == current_user:
            return {'status': 'failed', 'message': 'You may not report your own posts.'}
        if PostReport.query.filter_by(user_id=int(current_user.id), post_id=(int(post.id))).count() > 0:
            return {'status': 'failed', 'message': 'You have already reported this post. We have received your report and are assessing how best to handle the situation. Thank you for your patience.'}
        report = PostReport(post_id=int(post.id), user_id=int(current_user.id), body=str(request.form.get('explanation')),
                            timestamp=datetime.utcnow(), status=0)
    else:
        comment = Comment.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
        if comment.author == current_user:
            return {'status': 'failed', 'message': 'You may not report your own posts.'}
        if CommentReport.query.filter_by(user_id=int(current_user.id), comment_id=(int(comment.id))).count() > 0:
            return {'status': 'failed', 'message': 'You have already reported this post. We have received your report and are assessing how best to handle the situation. Thank you for your patience.'}
        report = CommentReport(comment_id=int(comment.id), user_id=int(current_user.id), body=str(request.form.get('explanation')),
                               timestamp=datetime.utcnow(), status=0)
    db.session.add(report)
    db.session.commit()
    send_dev_confirmed_report(current_user, str(request.form.get('explanation')))
    send_user_confirmed_report(current_user, str(request.form.get('explanation')))
    return {'status': 'success'}

@bp.route('/add_post', methods=['POST'])
@login_required
@restricted_user
def add_post():
    forum = Forum.query.filter_by(id=int(request.form.get('forum_id'))).first_or_404()
    post = Post(user_id=int(current_user.id), title=str(request.form.get('subject')),
                body=str(request.form.get('body')), forum_id=int(forum.id))
    db.session.add(post)
    db.session.commit()
    return {'status': 'success', 'id': str(post.id), 'html': str(post.render_html(int(request.form.get('type'))))}


@bp.route('/add_comment', methods=['POST'])
@login_required
@restricted_user
def add_comment():
    post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
    comment = Comment(user_id=int(current_user.id), body=str(request.form.get('body')), post_id=int(post.id))
    db.session.add(comment)
    db.session.commit()
    return {'status': 'success', 'html': str(comment.render_html())}

@bp.route('/edit_post', methods=['POST'])
@login_required
@restricted_user
def edit_post():
    post = Post.query.filter_by(id=int(request.form.get('post_id'))).first_or_404()
    # print(post)
    if current_user != post.author:
        # print('hi')
        return abort(403)
    post.body = str(request.form.get('body'))
    post.title = str(request.form.get('subject'))
    db.session.commit()
    return {'status': 'success'}

@bp.route('/edit_comment', methods=['POST'])
@login_required
@restricted_user
def edit_comment():
    comment = Comment.query.filter_by(id=int(request.form.get('comment_id'))).first_or_404()
    if current_user != comment.author:
        return abort(403)
    comment.body = str(request.form.get('body'))
    db.session.commit()
    return {'status': 'success'}

@bp.route('/delete_comment', methods=['POST'])
@login_required
@restricted_user
def delete_comment():
    comment = Comment.query.filter_by(id=int(request.form.get('comment_id'))).first_or_404()
    if comment.author == current_user:
        comment.delete()
        return {'status': 'success'}
    else:
        abort(403)

@bp.route('/upvote_comment', methods=['POST'])
@login_required
@restricted_user
def upvote_comment():
    comment = Comment.query.filter_by(id=int(request.form.get('comment_id'))).first_or_404()
    comment.upvote(current_user)
    return {'status': 'success'}

@bp.route('/downvote_comment', methods=['POST'])
@login_required
@restricted_user
def downvote_comment():
    comment = Comment.query.filter_by(id=int(request.form.get('comment_id'))).first_or_404()
    comment.downvote(current_user)
    return {'status': 'success'}

@bp.route('/join_forum', methods=['POST'])
@login_required
@restricted_user
def join_forum():
    forum = Forum.query.filter_by(id=int(request.form.get('forum_id'))).first_or_404()
    forum.join(current_user)
    return {'status': 'success'}

@bp.route('/leave_forum', methods=['POST'])
@login_required
@restricted_user
def leave_forum():
    forum = Forum.query.filter_by(id=int(request.form.get('forum_id'))).first_or_404()
    forum.leave(current_user)
    return {'status': 'success'}

@bp.route('/img_upload', methods=['POST'])
@login_required
def img_upload():
    file = request.files['file']
    if file.filename == '':
        return {'status':'failed', 'message':'We were unable to upload your image. Please try again or select a different image.'}
    else:
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        if current_user.directory is None or current_user.directory == '':
            current_user.directory = str(md5(str(current_user.id).encode('utf-8')).hexdigest())
        current_user.img = True
        resize_images(path, 'user', current_user)
        db.session.add(current_user)
        db.session.commit()
        send_email_edit_profile_changes(current_user, [{'field': 'user image',
                                                        'old': '(previously uploaded)',
                                                        'new': str(file.filename)}])
        flash("If your image does not appear to change, please try clearing your browser's cache")
        return {'status':'success'}

@bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    name = request.form.get('name')
    zip = str(request.form.get('zip'))
    city = str(request.form.get('city'))
    country = int(request.form.get('country'))
    user_bio = str(request.form.get('user_bio'))
    if current_user.is_recruiter:
        flash('Error!')
        return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))
    def get_changes():
        changes = []
        if email != current_user.email:
            changes.append({'field': 'email',
                            'old': current_user.email,
                            'new': email})
        if username != current_user.username:
            changes.append({'field': 'username',
                            'old': current_user.username,
                            'new': username})
        if name != current_user.name:
            changes.append({'field': 'name',
                            'old': current_user.name,
                            'new': name})
        if country != current_user.country_id:
            changes.append({'field': 'country',
                            'old': current_user.country.name,
                            'new': Country.query.filter_by(id=int(country)).first().name})
        if user_bio != current_user.about_me:
            changes.append({'field': 'bio',
                            'old': current_user.about_me,
                            'new': user_bio})
        if country == 235:
            if current_user.zip_code is not None:
                if zip != str(current_user.zip_code.name):
                    changes.append({'field': 'zip code',
                                    'old': str(current_user.zip_code.name),
                                    'new': str(zip)})
        else:
            if city.lower() != current_user.city.name.lower():
                changes.append({'field': 'city',
                                'old': str(current_user.city.name),
                                'new': str(city)})

        # print(changes)
        return changes
    # check if username already exists
    user_by_username = User.query.filter_by(username=username).first()
    if user_by_username is not None and user_by_username != current_user:
        flash('The username "' + str(username) + '" is already in use. Please enter a different one.')
        return redirect(url_for('main.user', username=current_user.username))

    # check if email already exists
    user_by_email = User.query.filter_by(email=email).first()
    if user_by_email is not None and user_by_email != current_user:
        flash('The email address "' + str(email) + '" is already in use. Please enter a different one.')
        return redirect(url_for('main.user', username=current_user.username))

    changes = get_changes()

    user_codes = check_entered_location(country, city, zip)
    if user_codes is None:
        return redirect(url_for('main.user', username=current_user.username))
    current_user.set_location(user_codes)
    current_user.suggest_forums()
    # update forums if necessary

    current_user.name = name
    current_user.username = username
    current_user.about_me = user_bio

    if len(changes) > 0:
        send_email_edit_profile_changes(current_user, changes)

    if current_user.email != email:
        current_user.email = email
        current_user.email_verified = False
        send_email_confirm_new_email(current_user)
        flash(
            'Check your email (and spam folder) to re-confirm your account after editing your email preferences.')

    db.session.add(current_user)
    db.session.commit()
    flash('Your profile has been updated.')
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/get_location', methods=['GET'])
@login_required
def get_location():
    if current_user.country_id == 235:
        return {'country': current_user.country_id, 'zip': current_user.zip_code.name}
    else:
        return {'country': current_user.country_id, 'city': current_user.city.name}

@bp.route('/get_comments', methods=['GET'])
@login_required
def get_comments():
    post = Post.query.filter_by(id=int(request.args.get('post_id'))).first_or_404()
    start = (int(request.args.get('set')) * 10)
    comments = post.get_comments(type=int(request.args.get('order')), start=start)
    html = ''
    if len(comments) > 0:
        for comment in comments:
            html += comment.render_html()
    else:
        html += "<div class='row' id='no-more-comments'><div class='col-sm-12 no-more-indicator'>That's all of the comments :(</div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/get_posts', methods=['GET'])
@login_required
def get_posts():

    forum = Forum.query.filter_by(id=int(request.args.get('forum_id'))).first_or_404()
    start = (int(request.args.get('set')) * 10)
    posts = forum.get_posts(type=int(request.args.get('order')), start=start)
    html = ''
    if len(posts) > 0:
        for post in posts:
            html += post.render_html(1)
    else:
        html += "<div class='row' id='no-more-posts'><div class='col-sm-12 no-more-indicator'>That's all of the posts :(</div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/get_posts_chat', methods=['GET'])
@login_required
def get_posts_chat():
    start = (int(request.args.get('set')) * 10)
    posts = current_user.get_followed_posts(type=int(request.args.get('order')), start=start)
    html = ''
    if len(posts) > 0:
        for post in posts:
            html += post.render_html(0)
    else:
        html += "<div class='row' id='no-more-posts'><div class='col-sm-12 no-more-indicator'>That's all of the posts :(</div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/load_more_jobs', methods=['GET'])
@login_required
def load_more_jobs():
    start = (int(request.args.get('set')) * 10)
    search = JobSavedSearch.query.filter_by(id=int(request.args.get('search_id'))).first_or_404()
    if search.user != current_user:
        return abort(403)
    jobs = search.get_jobs(type=int(request.args.get('order')), start=start)
    html = ''
    if len(jobs) > 0:
        for job in jobs:
            html += job.render_html()
    else:
        html += "<div class='row' id='no-more-jobs'><div class='col-sm-12 no-more-indicator'>That's all of the job listings for now :(</div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/load_more_messages', methods=['GET'])
@login_required
def load_more_messages():
    start = (int(request.args.get('set')) * 10)
    board = MessageBoard.query.filter_by(id=int(request.args.get('board_id'))).first_or_404()
    messages = board.get_messages(type=0, start=start)
    html = ''
    if len(messages) > 0:
        for message in messages[::-1]:
            html += message.render_html()
    else:
        html += "<div class='row' id='no-more-messages'><div class='col-sm-12 no-more-indicator'></div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/load_more_boards', methods=['GET'])
@login_required
def load_more_boards():
    start = (int(request.args.get('set')) * 10)
    boards = current_user.get_boards(type=0, start=start)
    html = ''
    if len(boards) > 0:
        for board in boards:
            html += board.render_html()
    else:
        html += "<div class='row' id='no-more-boards'><div class='col-sm-12 no-more-indicator'></div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/load_more_posts', methods=['GET'])
@login_required
def load_more_posts():
    start = (int(request.args.get('set')) * 10)
    style = int(request.args.get('style_type'))
    if int(style) != 0 and int(style) != 1:
        style = 0
    if int(request.args.get('forum_id')) == 0:
        posts = current_user.get_followed_posts(type=int(request.args.get('order')), start=start)
    else:
        forum = Forum.query.filter_by(id=int(request.args.get('forum_id'))).first_or_404()
        posts = forum.get_posts(type=int(request.args.get('order')), start=start)

    # if int(int(request.args.get('order'))) == 1:
    #     #     posts = [x[0] for x in posts]
    html = ''
    if len(posts) > 0:
        for post in posts:
            html += post.render_html(style)
    else:
        html += "<div class='row' id='no-more-posts'><div class='col-sm-12 no-more-indicator'>That's all of the posts :(</div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/get_job_listing_data', methods=['GET'])
@login_required
def get_job_listing_data():
    a = JobListingActivity.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if a.search.user != current_user:
        return abort(403)
    html = ''
    notes = JobListingNote.query.filter_by(job_id=a.job_id, search_id=a.search_id).order_by(JobListingNote.timestamp.desc())
    if notes.count() > 0:
        for j in notes.all():
            html += j.render_html()
    else:
        html += '<h5 class="no-posts">Your notes will appear here</h5>'
    return {'status': 'success', 'html': html, 'note_count':notes.count()}


@bp.route('/mark_quick_job_viewed', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def mark_quick_job_viewed():
    j = JobListingActivity.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if j.search.user != current_user:
        abort(403)
    if j.status == 0:
        ordering = JobListingActivity.query.filter_by(search_id=j.search_id, status=1)
        if ordering.count() > 0:
            last_order = ordering.order_by(JobListingActivity.order.desc()).first().order
        else:
            last_order = 0
        j.order = last_order + 1
        j.status = 1
    db.session.commit()
    return {'status': 'success'}


@bp.route('/submit_quick_apply', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def submit_quick_apply():
    job = JobListingActivity.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if job.search.user != current_user:
        return abort(403)
    if current_user.recruiter_visibility != 3:
        if current_user.recruiter_visibility < 3:
            flash('You must create a Professional Profile before applying to ILMJTCV Quick Apply jobs.')
            return {'status': 'failed', 'message': 'You must create a Professional Profile before applying to ILMJTCV Quick Apply jobs. You are being redirected now.', 'url':'/professional_profile'}
        else:
            flash('You must re-activate recruiter access before applying to ILMJTCV Quick Apply jobs.')
            return {'status': 'failed',
                    'message': 'You must re-activate recruiter access before applying to ILMJTCV Quick Apply jobs. You are being redirected now.',
                    'url': '/professional_profile'}
    if job.job.quick_apply != None:
        status = job.job.quick_apply.apply(current_user, request.form.get('custom_message'))
        if status:
            recruiters = [x.recruiter for x in job.job.recruiters]
            send_email_new_applicant(recruiters, job.job)
            send_email_confirm_apply(job.job, current_user)
            if JobListingActivity.query.filter_by(search_id=job.search_id, status=int(2)).count() > 0:
                last_order = JobListingActivity.query.filter_by(search_id=job.search_id,
                                                                status=int(2)).order_by(
                    JobListingActivity.order.desc()).first().order
                if last_order is None:
                    last_order = 0
            else:
                for o in JobListingActivity.query.filter_by(search_id=job.search_id, status=int(job.status)).all():
                    if o.order is not None and o.order > job.order:
                        o.order -= 1
                last_order = 0
            job.order = last_order + 1
            job.status = 2
            db.session.commit()
            return {'status': 'success', 'message': 'The recruiters for this job posting have been notified that you have '
                                                    'applied. They will reach out to you if they are interested in pursuing your candidacy.'}
        else:
            return {'status': 'failed',
                    'message': 'You have already applied to this job via a different saved job search.', 'url': '/job_search/' + str(job.search_id)}
    else:
        abort(404)


@bp.route('/remove_quick_apply', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def remove_quick_apply():
    job = JobListingActivity.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if job.search.user != current_user:
        return abort(403)
    if job.job.quick_apply != None:
        job.job.quick_apply.unapply(current_user)
        if JobListingActivity.query.filter_by(search_id=job.search_id, status=int(1)).count() > 0:
            last_order = JobListingActivity.query.filter_by(search_id=job.search_id,
                                                            status=int(1)).order_by(
                JobListingActivity.order.desc()).first().order
            if last_order is None:
                last_order = 0
        else:
            for o in JobListingActivity.query.filter_by(search_id=job.search_id, status=int(job.status)).all():
                if o.order is not None and o.order > job.order:
                    o.order -= 1
            last_order = 0
        job.order = last_order + 1
        job.status = 1
        send_email_applicant_removed(job.job, current_user)
        send_email_confirm_unapply(job.job, current_user)
        db.session.commit()
        return {'status': 'success', 'message': 'You have successfully withdrawn your application from this job posting. '}
    else:
        abort(404)

@bp.route('/edit_job_ss_note', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def edit_job_ss_note():
    note = JobSSNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    return {'status': 'success'}

@bp.route('/edit_job_listing_note', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def edit_job_listing_note():
    note = JobListingNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.edit(str(request.form.get('q')))
    return {'status': 'success'}


@bp.route('/del_job_ss_note', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def del_job_ss_note():
    note = JobSSNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    return {'status': 'success'}


@bp.route('/del_job_listing_note', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def del_job_listing_note():
    note = JobListingNote.query.filter_by(id=int(request.form.get('a'))).first_or_404()
    if not note.is_author(current_user):
        return abort(403)
    note.delete_note()
    return {'status': 'success'}


@bp.route('/read_notifications_all', methods=['GET'])
@login_required
def read_notifications_all():
    for n in current_user.notifications.filter_by(read=False):
        n.read = True
    db.session.commit()
    return {'status': 'success'}

@bp.route('/get_suggested')
@login_required
@restricted_user
def get_suggested():
    html = ''
    for f in current_user.suggested_forums:
        html += f.render_html()
    return {'status': 'success', 'html': html}


@bp.route('/deactivate_job_search', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def deactivate_job_search():
    j = JobSavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    # print(j)
    j.last_checked = datetime.utcnow()
    if j.user != current_user:
        abort(403)
    if j.status == 1:
        j.terminate()
        return {'status': 'success', 'url': str(url_for('main.professional_profile'))}
    else:
        return abort(404)


@bp.route('/delete_job_search', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def delete_job_search():
    j = JobSavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    j.last_checked = datetime.utcnow()
    if j.user != current_user:
        abort(403)
    if j.status == 0:
        j.delete_search()
        return {'status': 'success'}
    else:
        return abort(404)


@bp.route('/reactivate_job_search', methods=['POST'])
@login_required
@restricted_user
@restricted_completed
def reactivate_job_search():
    j = JobSavedSearch.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    j.last_checked = datetime.utcnow()
    if j.user != current_user:
        abort(403)
    if JobSavedSearch.query.filter_by(user_id=current_user.id, status=1).count() >= 3:
        return {'status': 'failed', 'message':'You already have 3 active job searches. You must deactivate a job search '
                                              'before you are able to reactivate this one.'}
    if j.status == 0:
        j.reactivate()
        return {'status': 'success'}
    else:
        return abort(404)

@bp.route('/get_deactivated', methods=['GET'])
@login_required
@restricted_user
def get_deactivated():
    html = ''
    searches = JobSavedSearch.query.filter_by(user_id=current_user.id, status=0).all()
    if len(searches) > 0:
        for i in searches:
            html += i.render_deactivated_html()
    else:
        html += '<div class="col-sm-12 no-more-indicator" style="margin-top: 15px; cursor: default">Nothing to show</div>'
    return {'status': 'success', 'html': html}


@bp.route('/get_profile_info_options/<num>', methods=['GET'])
@login_required
def get_profile_info_options(num):
    if int(num) == 1:
        option = Hobby
    elif int(num) == 2:
        option = Skill
    elif int(num) == 3:
        option = Interest
    elif int(num) == 4:
        option = Value
    else:
        abort(404)
    options = db.session.query(option).order_by(option.title.asc()).all()
    options = sorted(options, key= lambda r: current_user in r.users, reverse=True)
    html = ''
    for o in options:
        html += o.render_html()
    return {'status': 'success', 'html': html}

@bp.route('/update_profile_info_options', methods=['POST'])
@login_required
def update_profile_info_options():
    values = request.form.getlist('values[]')
    num = request.form.get('type')
    if int(num) == 1:
        option = Hobby
        current_user.hobbies = []
        changing = current_user.hobbies
    elif int(num) == 2:
        option = Skill
        current_user.skills = []
        changing = current_user.skills
    elif int(num) == 3:
        option = Interest
        current_user.interests = []
        changing = current_user.interests
    elif int(num) == 4:
        option = Value
        current_user.values = []
        changing = current_user.values
    else:
        abort(404)
    html = ''
    # print(values)
    for value in values:
        changing.append(option.query.filter_by(id=value).first())
        html += '<span class="no-highlight ">' + option.query.filter_by(id=value).first().title + '</span>'
    if len(values) == 0:
        html += '<span class="no-highlight" style="background-color: #f8f8ff6b !important;">Nothing Selected</span>'
    db.session.commit()
    return {'status':'success', 'html': html}


@bp.route('/start_new_convo', methods=['POST'])
@login_required
def start_new_convo():
    recipient = User.query.filter_by(id=int(request.form.get('r_id'))).first_or_404()
    subject = request.form.get('s')
    message = request.form.get('q')
    board = MessageBoard(subject=subject, recruiting=False)
    db.session.add(board)
    db.session.commit()
    board.add_member(current_user)
    board.add_member(recipient)
    board.send_message(current_user, message)
    return {'status': 'success', 'id': str(board.id)}


@bp.route('/get_existing_convos', methods=['GET'])
@login_required
def get_existing_convos():
    recipient = User.query.filter_by(id=int(request.args.get('r_id'))).first_or_404()
    boards = [x for x in current_user.message_boards if not x.recruiting and recipient in x.members]
    html = ''
    for board in boards:
        html += board.render_html()
    return {'status': 'success', 'html': html, 'name': recipient.name}


@bp.route('/get_similar_people', methods=['GET'])
@login_required
@restricted_user
def get_similar_people():
    if current_user.completed < 2:
        return {'status': 'success'}
    start = int(request.args.get('set')) * 10
    existing = [int(x) for x in request.args.getlist('existing')]
    people = current_user.similar_people(start, existing=existing)
    html = ''
    if len(people) > 0:
        for i in range(len(people)):
            html += people[i][0].render_social_card(people[i][1])
            if i % 2 == 1:
                html += '<div class="clearfix visible-md visible-lg visible-sm"></div>'
    else:
        if start == 0:
            html += "<div class='row' id='no-results' style='margin-bottom: 30px'><div class='col-sm-12 no-more-indicator' style='text-transform: uppercase'>We were unable to find any suggested connections for you. <br>Try editing your <a class='menu-item' href='/user/" + current_user.username + "'> profile information</a> or adding job searches so we can find people with similarities to you!</div></div>"
        else:
            html += "<div class='row' id='no-results' style='margin-bottom: 30px'><div class='col-sm-12 no-more-indicator'>That's all of our suggested connections! Please continue to check back here for more.</div></div>"

    return {'status': 'success', 'html': html}


@bp.route('/get_resources', methods=['GET'])
@login_required
@restricted_user
def get_resources():
    start = int(request.args.get('set')) * 10
    type = int(request.args.get('ordering'))
    resources = current_user.get_resources(type, start)
    html = ''
    if len(resources) > 0:
        if start == 0:
            if type == 1 or type == 2:
                html += "<div class='row' id='area-specific'><div class='col-sm-12 no-more-indicator' style='text-transform: uppercase; text-align:left; margin: 5px 0 !important'>for " + current_user.state.name +":</div></div>"
        for i in range(len(resources)):
            html += resources[i].render_html()
            if i % 2 == 1:
                html += '<div class="clearfix visible-md visible-lg visible-sm"></div>'
    else:
        if start == 0:
            html += "<div class='row' id='no-results' style='margin-bottom: 30px'><div class='col-sm-12 no-more-indicator' style='text-transform: uppercase'>We are working on adding resources for this category.<tr>Please continue to check back here.</div></div>"
        else:
            html += "<div class='row' id='no-results' style='margin-bottom: 30px'><div class='col-sm-12 no-more-indicator'>That's all we've got for now! Check back later for more.</div></div>"
    url = '/resources?type=' + str(type)
    return {'status': 'success', 'html': html, 'url': url}


@bp.route('/load_more_blogs', methods=['GET'])
def load_more_blogs():
    start = (int(request.args.get('set')) * 3)
    blogs = BlogPost.query.order_by(BlogPost.posted.desc()).all()[int(start): int(start) + 3]
    html = ''
    if len(blogs) > 0:
        for blog in blogs:
            html += blog.render_preview()
    else:
        html += "<div class='row' id='no-more-posts' style='text-transform:uppercase'><div class='col-sm-12 no-more-indicator'>More blogs coming soon</div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/load_more_partners', methods=['GET'])
@login_required
@restricted_user
def load_more_partners():
    start = (int(request.args.get('set')) * 10)
    partners = ExclusivePartner.query.order_by(ExclusivePartner.posted.desc()).all()[int(start): int(start) + 10]
    html = ''
    if len(partners) > 0:
        for i in range(len(partners)):
            if i % 2 == 0:
                html += '<div class="clearfix visible-md visible-lg visible-sm"></div>'
            html += partners[i].render_preview()
    else:
        html += "<div class='row' id='no-more-posts'><div class='col-sm-12 no-more-indicator'></div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/get_partner_modal', methods=['GET'])
@login_required
@restricted_user
def get_partner_modal():
    partner = ExclusivePartner.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    html = partner.render_html()
    return {'status':'success', 'html': html}


@bp.route('/open_partner/<id>')
@login_required
@restricted_user
def open_partner(id):
    e = ExclusivePartner.query.filter_by(id=int(id)).first_or_404()
    a = PartnerClicks(partner_id=e.id, user_id=current_user.id, timestamp=datetime.utcnow())
    db.session.add(a)
    db.session.commit()
    return redirect(e.link)


@bp.route('/load_more_events', methods=['GET'])
@login_required
@restricted_user
def load_more_events():
    start = (int(request.args.get('set')) * 5)
    type = int(request.args.get('ordering'))
    events = current_user.get_events(type, start)
    url = '/events?type=' + str(type)
    html = ''
    if len(events) > 0:
        for i in range(len(events)):
            if i % 3 == 2:
                html += '<div class="clearfix visible-md visible-lg visible-sm"></div>'
            html += events[i].render_preview()
    else:
        html += "<div class='row' id='no-more-posts'><div class='col-sm-12 no-more-indicator'>We'll be adding more events soon!</div></div>"
    return {'status': 'success', 'html': html, 'url': url}

@bp.route('/get_event_modal', methods=['GET'])
@login_required
@restricted_user
def get_event_modal():
    event = Event.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    html = event.render_html()
    return {'status':'success', 'html': html}

@bp.route('/rsvp_event', methods=['POST'])
@login_required
@restricted_user
def rsvp_event():
    e = Event.query.filter_by(id=int(request.form.get('e_id'))).first_or_404()
    response = e.rsvp(current_user)
    if response:
        send_email_event_rsvp(current_user, e)
    else:
        send_email_event_unrsvp(current_user, e)
    return {'status': 'success'}


@bp.route('/get_upcoming_appointments', methods=['GET'])
@login_required
@restricted_user
def get_upcoming_appointments():
    offset = str(request.args.get('offset'))
    start = int(request.args.get('set'))
    d = datetime.utcnow()
    a = Appointment.query.filter(Appointment.start_time >= d, Appointment.mentor_id == current_user.mentor_profile.id).order_by(Appointment.start_time.asc()).all()[int(start) * 10: int(start) * 10 + 10]
    html = ''
    if len(a) > 0:
        for i in a:
            html += i.render_upcoming_preview()
    else:
        if start > 0:
            html += "<div class='row' id='no-more-upcoming'><div class='col-sm-12 no-more-indicator'>nothing else to show</div><div class='filler'></div><div class='filler'></div></div>"
        else:
            html += "<div class='row' id='no-more-upcoming'><div class='col-sm-12 no-more-indicator'>NO UPCOMING APPOINTMENTS</div><div class='filler'></div><div class='filler'></div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/get_past_appointments', methods=['GET'])
@login_required
@restricted_user
def get_past_appointments():
    offset = str(request.args.get('offset'))
    start = int(request.args.get('set'))
    print(start)
    d = datetime.utcnow()
    a = db.session.query(Appointment).join(AppointmentParticipantAssociations, (AppointmentParticipantAssociations.c.appointment_id == Appointment.id)
                                           ).filter(Appointment.start_time <= d,
                                                    Appointment.mentor_id == current_user.mentor_profile.id
                                                    ).all()[int(start) * 10: int(start) * 10 + 10]
    html = ''
    if len(a) > 0:
        for i in a:
            html += i.render_past_preview()
    else:
        html += "<div class='row' id='no-more-past'><div class='col-sm-12 no-more-indicator'>NO PAST APPOINTMENTS TO REVIEW</div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/get_upcoming_appointments_mentee', methods=['GET'])
@login_required
@restricted_user
def get_upcoming_appointments_mentee():
    start = int(request.args.get('set'))
    d = datetime.utcnow()
    a = db.session.query(Appointment).join(AppointmentParticipantAssociations,
                                           (AppointmentParticipantAssociations.c.appointment_id == Appointment.id)
                                           ).filter(Appointment.start_time >= d,
                                                    AppointmentParticipantAssociations.c.user_id == current_user.id
                                                    ).order_by(Appointment.start_time.asc()).all()[int(start) * 10: int(start) * 10 + 10]
    html = ''
    if len(a) > 0:
        for i in a:
            html += i.render_upcoming_preview_mentee()
    else:
        if start > 0:
            html += "<div class='row' id='no-more-upcoming'><div class='col-sm-12 no-more-indicator'>nothing else to show</div><div class='filler'></div><div class='filler'></div></div>"
        else:
            html += "<div class='row' id='no-more-upcoming'><div class='col-sm-12 no-more-indicator'>NO UPCOMING APPOINTMENTS</div><div class='filler'></div><div class='filler'></div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/get_past_appointments_mentee', methods=['GET'])
@login_required
@restricted_user
def get_past_appointments_mentee():
    start = int(request.args.get('set'))
    d = datetime.utcnow()
    a = db.session.query(Appointment).join(AppointmentParticipantAssociations, (AppointmentParticipantAssociations.c.appointment_id == Appointment.id)
                                           ).filter(Appointment.start_time <= d,
                                                    AppointmentParticipantAssociations.c.user_id == current_user.id
                                                    ).order_by(Appointment.start_time.desc()).all()[int(start) * 10: int(start) * 10 + 10]
    html = ''
    if len(a) > 0:
        for i in a:
            html += i.render_past_preview_mentee()
    else:
        html += "<div class='row' id='no-more-past'><div class='col-sm-12 no-more-indicator'>NO PAST APPOINTMENTS TO REVIEW</div></div>"
    return {'status': 'success', 'html': html}

@bp.route('/add_available_times', methods=['POST'])
@login_required
@restricted_user
def add_available_times():
    offset = str(request.form.get('offset'))
    start = str(request.form.get('start'))
    end = str(request.form.get('end'))
    date = str(request.form.get('date'))
    start_string = date + ' ' +  start + ':00'
    end_string = date + ' ' + end + ':00'
    if offset[0] == '-':
        start_stamp = datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S') + timedelta(minutes=int(offset[1:]))
        end_stamp = datetime.strptime(end_string, '%m/%d/%Y %H:%M:%S') + timedelta(minutes=int(offset[1:]))
    else:
        start_stamp = datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S') + timedelta(minutes=int(offset[1:]))
        end_stamp = datetime.strptime(end_string, '%m/%d/%Y %H:%M:%S') + timedelta(minutes=int(offset[1:]))
    duration = str(end_stamp - start_stamp).split(':')
    sessions = int(((int(duration[0]) * 60) + (int(duration[1]))) / 30)
    for i in range(sessions):
        if Appointment.query.filter_by(mentor_id=current_user.mentor_profile.id,
                                       start_time=start_stamp + timedelta(minutes=30*i),
                                       end_time=start_stamp + timedelta(minutes=30*(i + 1))).count() == 0:
            appointment = Appointment(start_time=start_stamp + timedelta(minutes=30*i),
                                      end_time=start_stamp + timedelta(minutes=30*(i + 1)),
                                      status=0,
                                      mentor_id=current_user.mentor_profile.id
                                      )
            db.session.add(appointment)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/get_edit_upcoming_modal', methods=['GET'])
@login_required
@restricted_user
def get_edit_upcoming_modal():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if a.is_mentor(current_user):
        html = a.render_html_modal()
        return {'status': 'success', 'html': html}
    elif current_user in a.participants:
        html = a.render_html_modal_mentee()
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed', 'message': 'restricted'}


@bp.route('/load_more_appointment_notes', methods=['GET'])
@login_required
@restricted_user
def load_more_appointment_notes():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    start = int(request.args.get('set')) * 10
    if current_user == a.mentor.user:
        notes = a.get_notes(start)
    elif current_user in a.participants:
        notes = a.get_mentee_notes(start)
    else:
        return {'status': 'failed', 'message':'restricted'}
    html = ''
    if len(notes) > 0:
        for note in notes:
            html += note.render_html()
    else:
        html += "<div class='row' id='no-more-notes'><div class='col-sm-12 no-more-indicator'></div></div>"
    return {'status': 'success', 'html': html}


@bp.route('/post_participant_note', methods=['POST'])
@login_required
@restricted_user
def post_participant_note():
    a = Appointment.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    a.add_note(request.form.get('q'), current_user)
    if current_user == a.mentor.user:
        notes = a.get_notes(0)
    else:
        notes = a.get_mentee_notes(0)
    html = ''
    for note in notes:
        html += note.render_html()
    return {'status': 'success', 'html': html}


@bp.route('/get_participant_messages', methods=['GET'])
@login_required
@restricted_user
def get_participant_messages():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if not a.is_mentor(current_user) and current_user not in a.participants:
        return {'status': 'failed', 'message': 'restricted'}
    html = a.render_messages_board()
    return {'status': 'success', 'html': html}

@bp.route('/get_participant_notes', methods=['GET'])
@login_required
@restricted_user
def get_participant_notes():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if current_user == a.mentor.user:
        html = a.render_notes_board()
        return {'status': 'success', 'html': html}
    elif current_user in a.participants:
        html = a.render_notes_board_mentee()
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed', 'message':'restricted'}



@bp.route('/cancel_appointment', methods=['POST'])
@login_required
@restricted_user
def cancel_appointment():
    a = Appointment.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if not a.is_mentor(current_user) and a.participants[0] != current_user:
        return {'status': 'failed', 'message': 'restricted'}
    if len(a.participants) > 0:
        if a.enough_time_start(5):
            if a.is_mentor(current_user):
                send_email_appointment_cancelled_mentee(a.participants[0], a, False)
                send_email_appointment_cancelled_mentor(a.mentor.user, a, True)
            else:
                c = Appointment(mentor_id=a.mentor_id, start_time=a.start_time, end_time=a.end_time,
                                status=0)
                db.session.add(c)
                db.session.commit()
                send_email_appointment_cancelled_mentee(a.participants[0], a, True)
                send_email_appointment_cancelled_mentor(a.mentor.user, a, False)
            a.delete_appointment()
            return {'status': 'success'}
        else:
            return {'status': 'failed', 'message': 'You are unable to cancel an appointment within 5 minutes of its start time.'}
    else:
        a.delete_appointment()
        return {'status': 'success'}


@bp.route('/register_appointment', methods=['POST'])
@login_required
@restricted_user
def register_appointment():
    a = Appointment.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if db.session.query(Appointment).join(AppointmentParticipantAssociations, (Appointment.id == AppointmentParticipantAssociations.c.appointment_id)).filter(
        Appointment.start_time == a.start_time,
        AppointmentParticipantAssociations.c.user_id == current_user.id
    ).count() > 0:
        return {'status': 'failed', 'message': 'You already have an appointment booked during that time slot.'}
    if current_user.is_mentor():
        if Appointment.query.filter(
                Appointment.start_time == a.start_time,
                Appointment.mentor_id == current_user.mentor_profile.id
        ).count() > 0:
            return {'status': 'failed', 'message': 'You already have an appointment booked during that time slot.'}
    sign_up = a.sign_up(current_user)
    if sign_up:
        send_email_appointment_confirmed(current_user, a)
        send_email_appointment_filled(a.mentor.user, a)
        return {'status': 'success'}
    else:
        return {'status': 'failed', 'message': 'The appointment seems to be booked already. Please try again.'}


@bp.route('/update_mentor_info', methods=['POST'])
@login_required
@restricted_user
def update_mentor_info():
    if current_user.mentor_profile is not None:
        if request.form.get('password') != None and len(request.form.get('password')) > 0:
            current_user.mentor_profile.zoom_password = request.form.get('password')
        else:
            current_user.mentor_profile.zoom_password = None
        current_user.mentor_profile.zoom_link = request.form.get('link')
        current_user.mentor_profile.bio = request.form.get('bio')
        current_user.mentor_profile.linked_in = request.form.get('linkedin')
        db.session.commit()
        send_email_mentor_info_update(current_user)
        return {'status': 'success'}
    else:
        return {'status': 'failed', 'message': 'restricted'}


@bp.route('/get_news_articles', methods=['GET'])
def get_news_articles():
    html = ''
    start = int(request.args.get('set')) * 6
    news = NewsArticle.query.order_by(NewsArticle.added.asc()).all()[start: start + 6]
    if len(news) > 0:
        if start > 0:
            html += '<div class="clearfix visible-md visible-lg visible-sm"></div>'
        for n in range(len(news)):
            html += news[n].render_html()
            if n % 3 == 2:
                html += '<div class="clearfix visible-md visible-lg"></div>'
            if n % 2 == 1:
                html += '<div class="clearfix visible-sm"></div>'
    else:
        html += "<div class='row' id='no-more-news'><div class='col-sm-12 no-more-indicator'></div></div>"

    return {'status': 'success', 'html': html}

@bp.route('/get_day_slots', methods=['GET'])
@login_required
@restricted_user
def get_day_slots():
    date = datetime.strptime(request.args.get('date'), "%m/%d/%Y")
    appointments = Appointment.query.filter(Appointment.start_time >= date,
                                            Appointment.end_time <= date + timedelta(hours=24),
                                            Appointment.status == 0).all()
    if len(appointments) > 0:
        slots = []
        html = ''
        for a in appointments:
            if a.start_time not in [x.start_time for x in slots]:
                slots.append(a)
        print(slots)
        html += render_template('main/mentorship/sessions/slots.html', slots=slots)
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'success', 'html': "<div class='row' id='no-more-appointments'><div class='col-sm-12 no-more-indicator'>NO AVAILABILITY<br>Please select a different day.</div></div"}


@bp.route('/get_mentor_options', methods=['GET'])
@login_required
@restricted_user
def get_mentor_options():
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d %H:%M:%S')
    appointments = Appointment.query.filter(
        Appointment.start_time == date,
        Appointment.status == 0,
    ).all()
    if len(appointments) > 0:
        html = render_template('main/mentorship/sessions/participant/mentor_options.html', appointments=appointments)
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed'}

@bp.route('/get_join_modal', methods=['GET'])
@login_required
@restricted_user
def get_join_modal():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if a.join_time():
        if current_user == a.mentor.user or current_user in a.participants:
            html = a.get_join_modal()
            return {'status': 'success', 'html': html}
        else:
            return {'status': 'failed', 'message': 'restricted'}
    else:
        return {'status': 'failed', 'message': 'Appointment is either over or its start time is in more than 5 minutes.'}


@bp.route('/get_rating_modal', methods=['GET'])
@login_required
@restricted_user
def get_rating_modal():
    a = Appointment.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    if current_user in a.participants:
        html = a.get_rating_modal()
        return {'status': 'success', 'html': html}
    else:
        return {'status': 'failed', 'message': 'restricted'}


@bp.route('/post_appointment_rating', methods=['POST'])
@login_required
@restricted_user
def post_appointment_rating():
    a = Appointment.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    if current_user in a.participants:
        print(float(request.form.get('rating')))
        a.add_rating(float(request.form.get('rating')), current_user)
        return {'status': 'success'}
    else:
        return {'status': 'failed', 'message': 'restricted'}


@bp.route('/add_mentee_info', methods=['POST'])
@login_required
@restricted_user
def add_mentee_info():
    changes = []
    resume = request.files.get('resume')
    if resume.filename != '':
        path = 'app/static/uploads/' + str(current_user.username) + '.pdf'
        os.makedirs('app/static/uploads/', exist_ok=True)
        resume.save(path)
        filename = upload_file(file=path, user=current_user, bucket='user', extension='application/pdf', name='resume')
        os.remove(path=path)
        current_user.directory = filename
        current_user.resume = True
        changes.append({'field': 'resume',
                            'old': 'Previously Uploaded Resume',
                            'new': "Resume Uploaded Just Now"})
    if len(request.form.get('linked_in_link')) > 0:
        if current_user.recruiting_profile is None:
            profile = RecruitingProfile(user_id=current_user.id)
            db.session.add(profile)
        else:
            profile = current_user.recruiting_profile
            changes.append({'field': 'LinkedIn Link',
                            'old': profile.linked_in,
                            'new': str(request.form.get('linked_in_link'))})
        profile.linked_in = str(request.form.get('linked_in_link'))
    else:
        if current_user.recruiting_profile is not None:
            changes.append({'field': 'LinkedIn Link',
                            'old': current_user.recruiting_profile.linked_in,
                            'new': 'null'})
            current_user.recruiting_profile.linked_in = None

    send_email_edit_profile_changes(current_user, changes)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/apply_mentor', methods=['POST'])
@login_required
@restricted_user
def apply_mentor():
    if current_user.mentor_profile is None:
        profile = MentorProfile(user_id=current_user.id)
        profile.zoom_link = request.form.get('zoom_link')
        profile.zoom_password = request.form.get('zoom_password')
        profile.linked_in = request.form.get('linked_in_link')
        profile.bio = request.form.get('bio')
        profile.why = request.form.get('why')
        db.session.add(profile)
        db.session.commit()
        send_email_mentor_app_receivied(current_user)
        return {'status': 'success'}
    else:
        return {'status': 'failed', 'message': 'An error has occurred. Either you have already been approved to be an ILMJTCV Mentor or your application status is pending.'}
