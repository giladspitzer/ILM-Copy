from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from app import db
from app.admin import bp
from app.models import Resource, Event, MentorProfile
from datetime import datetime
import os
from app.tasks import upload_file
from PIL import ImageOps, Image
from app.models import Event, SpeakerProfile, Industry, ResourceType, Resource, CustomEmail, User, NewsArticle
from app.background.emails import send_email_custom_message_test, send_email_custom_message, \
    send_email_custom_sending_done, send_email_to_devs
from app.main.emails import send_email_mentor_approved, send_email_mentor_rejected


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.admin:
            abort(403)

@bp.route('/resources')
@login_required
def resources():
    return render_template('admin//resources.html', resources=Resource.query.all())

@bp.route('/event/<id>')
@login_required
def event(id):
    e = Event.query.filter_by(id=int(id)).first_or_404()
    return render_template('admin/_event.html', event=e)


@bp.route('/events')
@login_required
def events():
    return render_template('admin/events.html', speakers=SpeakerProfile.query.all(), events=Event.query.all())

@bp.route('/news')
@login_required
def news():
    return render_template('admin/news.html', stories=NewsArticle.query.order_by(NewsArticle.added.desc()).all())


@bp.route('/add_news', methods=['POST'])
@login_required
def add_news():
    title = str(request.form.get('news_title'))
    description = str(request.form.get('news_description'))
    link = str(request.form.get('news_link'))
    file = request.files['news_img']
    if file.filename == '':
        return {'status': 'failed',
                'message': 'We were unable to upload your image. Please try again or select a different image.'}
    else:
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='news', extension='image/jpg', name=title.replace(' ', '_'))
        os.remove(path)
    path = title.replace(' ', '_') + '.jpg'
    s = NewsArticle(title=title, description=description, img=path, link=link, added=datetime.utcnow())
    db.session.add(s)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/edit_news', methods=['POST'])
@login_required
def edit_news():
    s = NewsArticle.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    s.title = str(request.form.get('news_title_edit'))
    s.description = str(request.form.get('news_description_edit'))
    s.link = str(request.form.get('news_link_edit'))
    file = request.files['news_img_edit']
    if file.filename != '':
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='news', extension='image/jpg', name=s.title.replace(' ', '_'))
        os.remove(path)
        s.img = s.title.replace(' ', '_') + '.jpg'
    db.session.commit()
    return {'status': 'success'}


@bp.route('/delete_news', methods=['POST'])
@login_required
def delete_news():
    s = NewsArticle.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    s.delete_news()
    return {'status': 'success'}


@bp.route('/get_news_edit_modal', methods=['GET'])
@login_required
def get_news_edit_modal():
    s = NewsArticle.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    return {'status': 'success', 'html': s.render_edit_modal()}




@bp.route('/emails')
@login_required
def emails():
    return render_template('admin/email.html', emails=CustomEmail.query.all())

@bp.route('/get_edit_email', methods=['GET'])
@login_required
def get_edit_email():
    email = CustomEmail.query.filter_by(id=request.args.get('id')).first_or_404()
    if email.status < 1:
        return {'status': 'success', 'html': email.render_edit_html(), 'audience': email.audience, 'message': email.message}
    else:
        return {'status': 'failed', 'message': 'Email already sent for approval.'}

@bp.route('/add_email', methods=['POST'])
@login_required
def add_email():
    e = CustomEmail(prefix=request.form.get('prefix'), subject=request.form.get('subject'), message=request.form.get('message'), timestamp=datetime.utcnow(),
                    header_text=request.form.get('header'), button_link=request.form.get('button_link'), button_text=request.form.get('button_text'),
                    audience=int(request.form.get('audience')), user_id=current_user.id, status=0)
    db.session.add(e)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/edit_email', methods=['POST'])
@login_required
def edit_email():
    e = CustomEmail.query.filter_by(id=request.form.get('id')).first_or_404()
    if e.status < 1:
        e.prefix = request.form.get('prefix')
        e.subject = request.form.get('subject')
        e.message = request.form.get('message')
        e.header_text = request.form.get('header')
        e.button_link = request.form.get('button_link')
        e.button_text = request.form.get('button_text')
        e.audience = int(request.form.get('audience'))
        db.session.commit()
    else:
        return {'status': 'failed', 'message': 'Email already sent for approval.'}
    return {'status': 'success'}


@bp.route('/delete_email', methods=['POST'])
@login_required
def delete_email():
    e = CustomEmail.query.filter_by(id=request.form.get('id')).first_or_404()
    if e.status < 2:
        e.delete_email()
    else:
        return {'status': 'failed', 'message': 'Email already sent.'}
    return {'status': 'success'}


@bp.route('/preview_email/<id>')
@login_required
def preview_email(id):
    email = CustomEmail.query.filter_by(id=int(id)).first_or_404()
    return render_template('background/email/custom/custom_message.html', email=email, user=current_user)


@bp.route('/send_email/<id>')
@login_required
def send_email(id):
    email = CustomEmail.query.filter_by(id=int(id)).first_or_404()
    if email.status == 0:
        email.status = 1
        db.session.commit()
        for i in [User.query.filter_by(id=724).first(), User.query.filter_by(id=727).first()]:
            send_email_custom_message_test(i, len(email.get_audience()), email)
        flash('Sent')
        return redirect(url_for('admin.emails'))
    else:
        flash('Already Sent or Pending Approval')
        return redirect(url_for('admin.emails'))

@bp.route('/confirm_send_email/<token>')
@login_required
def confirm_send_email(token):
    email = CustomEmail.verify_sending_confirmation_token(token)
    if email is not None and email.status == 1:
        email.status = 2
        db.session.commit()
        users = email.get_audience()
        for user in users:
            send_email_custom_message(user, email)
        for i in [User.query.filter_by(id=724).first(), User.query.filter_by(id=727).first()]:
            send_email_custom_sending_done(i, len(users), email)
        flash('Sent')
        return redirect(url_for('admin.emails'))
    else:
        flash('Already Sent or Pending Approval')
        return redirect(url_for('admin.emails'))


@bp.route('/add_speaker', methods=['POST'])
@login_required
def add_speaker():
    name = str(request.form.get('speaker_name'))
    title = str(request.form.get('speaker_title'))
    email = str(request.form.get('speaker_email'))
    linkedin = str(request.form.get('speaker_linkedin'))
    bio = str(request.form.get('description'))
    file = request.files['speaker_img']
    if file.filename == '':
        return {'status': 'failed',
                'message': 'We were unable to upload your image. Please try again or select a different image.'}
    else:
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='speakers', extension='image/jpg', name=name.replace(' ', '_'))
        os.remove(path)
    s = SpeakerProfile(name=name, bio=bio, img=name.replace(' ', '_'), title=title, linkedin=linkedin, email=email)
    db.session.add(s)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/edit_speaker', methods=['POST'])
@login_required
def edit_speaker():
    s = SpeakerProfile.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    s.name = str(request.form.get('speaker_name'))
    s.title = str(request.form.get('speaker_title'))
    s.email = str(request.form.get('speaker_email'))
    s.linkedin = str(request.form.get('speaker_linkedin'))
    s.bio = str(request.form.get('description'))
    file = request.files['speaker_img']
    if file.filename != '':
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='speakers', extension='image/jpg', name=s.name.replace(' ', '_'))
        os.remove(path)
    db.session.commit()
    return {'status': 'success'}

@bp.route('/create_event', methods=['POST'])
@login_required
def create_event():
    title = str(request.form.get('event_title'))
    description = str(request.form.get('description'))
    link = str(request.form.get('event_link'))
    start = datetime.strptime(request.form.get('start-time'), '%Y-%m-%dT%H:%M')
    end = datetime.strptime(request.form.get('end-time'), '%Y-%m-%dT%H:%M')
    recorded = True if str(request.form.get('recorded')) == 'on' else False
    industries = request.form.getlist('industry')
    speakers = request.form.getlist('speakers')
    file = request.files['event_img']
    if file.filename == '':
        return {'status': 'failed',
                'message': 'We were unable to upload your image. Please try again or select a different image.'}
    else:
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='events', extension='image/jpg', name=title.replace(' ', '_'))
        os.remove(path)
    e = Event(title=title, description=description, external_link=link, time_start=start, time_end=end, img=title.replace(' ', '_'),
              recorded=recorded)
    db.session.add(e)
    if '0' not in industries or len(industries) == 0:
        for i in industries:
            e.industries.append(Industry.query.filter_by(id=int(i)).first())
    for s in speakers:
        e.speakers.append(SpeakerProfile.query.filter_by(id=int(s)).first())
    db.session.commit()
    return {'status': 'success'}

@bp.route('/delete_event', methods=['POST'])
@login_required
def delete_event():
    e = Event.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    e.delete_event()
    send_email_to_devs('event (' + e.title + ')deleted by (' + current_user.name + ')')
    flash('Event Deleted')
    return {'status': 'success'}


@bp.route('/edit_event', methods=['POST'])
@login_required
def edit_event():
    print(request.form)
    e = Event.query.filter_by(id=int(request.form.get('e_id'))).first()
    changes = False
    e.title = str(request.form.get('event_title'))
    e.description = str(request.form.get('description'))
    e.external_link = str(request.form.get('event_link'))
    e.recorded = True if str(request.form.get('recorded')) == 'on' else False
    e.recorded_link = str(request.form.get('recorded_link'))
    e.industries = []
    for i in request.form.getlist('industries'):
        e.industries.append(Industry.query.filter_by(id=int(i)).first())
    e.speakers = []
    for j in request.form.getlist('speakers'):
        e.speakers.append(SpeakerProfile.query.filter_by(id=int(j)).first())

    if datetime.strptime(request.form.get('start-time'), '%Y-%m-%dT%H:%M') != e.time_start:
        e.time_start = datetime.strptime(request.form.get('start-time'), '%Y-%m-%dT%H:%M')
        changes = True
    if datetime.strptime(request.form.get('end-time'), '%Y-%m-%dT%H:%M') != e.time_end:
        e.time_end = datetime.strptime(request.form.get('end-time'), '%Y-%m-%dT%H:%M')
        changes = True

    db.session.commit()

    file = request.files['event_img_edit']
    if file.filename != '':
        path = 'app/static/uploads/' + file.filename
        os.makedirs('app/static/uploads/', exist_ok=True)
        file.save(path)
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image.save(path)
        upload_file(file=path, user=current_user, bucket='events', extension='image/jpg', name=str(request.form.get('event_title')).replace(' ', '_'))
        os.remove(path)

    if changes:
        for user in e.rsvps:
            print('send email updated')

    return {'status': 'success'}

@bp.route('/get_speakers', methods=['GET'])
@login_required
def get_speakers():
    html = ''
    for i in SpeakerProfile.query.all():
        html += '<option value="' + str(i.id) + '" data-tokens="' + str(i.name) + '">' + str(i.name) + '</option>'
    return {'status': 'success', 'html': html}

@bp.route('/get_speaker_edit_modal', methods=['GET'])
@login_required
def get_speaker_edit_modal():
    s = SpeakerProfile.query.filter_by(id=int(request.args.get('id'))).first_or_404()
    return {'status': 'success', 'html': s.render_edit_modal()}


@bp.route('/add_resource', methods=['GET'])
@login_required
def add_resource():
    titles = ['U.S. Small Business Association', 'IRS', 'Consumer Finance', 'Morning Brew']
    links = ['https://www.sba.gov/page/coronavirus-covid-19-small-business-guidance-loan-resources', 'https://www.irs.gov/coronavirus/get-my-payment', 'https://www.consumerfinance.gov/coronavirus/mortgage-and-housing-assistance/mortgage-relief/', 'https://www.morningbrew.com/daily/stories/2020/07/15/not-suck-cold-emailing?utm_source=morning_brew']
    imgs = ['https://tomcopelandblog.com/wp-content/uploads/2020/04/AGF-l7_cyxF7JDiZ5t7ZJtTG8i8cSapQRrc9-rFviws900-c-k-c0xffffffff-no-rj-mo.jpg', 'https://www.irs.gov/pub/image/logo_small.jpg', 'https://iscinc.github.io/government/assets/img/featured-orgs/cfpb.png', 'https://pbs.twimg.com/profile_images/1177672352588599296/OLUd0Htt_200x200.png']
    descriptions = ['Coronavirus (COVID-19): Small Business Guidance & Loan Resources', 'Check on the status of your Economic Impact Payment', 'Learn about mortgage relief options and protections', 'How to Cold Email Your Way into Your Dream Job']
    types = [2, 2, 3, 1]
    for i in range(len(titles)):
        a = Resource(title=titles[i], description=descriptions[i], link=links[i], added=datetime.utcnow(), active=True,
                     img=imgs[i])
        db.session.add(a)
        a.types.append(ResourceType.query.filter_by(id=int(types[i])).first())
        db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/confirm_mentor', methods=['POST'])
@login_required
def confirm_mentor():
    m = MentorProfile.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    m.status = 1
    send_email_mentor_approved(m.user)
    flash('Mentor Approved')
    return {'status': 'success'}

@bp.route('/reject_mentor', methods=['POST'])
@login_required
def reject_mentor():
    m = MentorProfile.query.filter_by(id=int(request.form.get('id'))).first_or_404()
    send_email_mentor_rejected(m.user)
    m.delete_mentor_profile()
    flash('Mentor Rejected')
    return {'status': 'success'}

@bp.route('/mentors')
@login_required
def mentors():
    return render_template('admin/mentors.html', mentors=MentorProfile.query.filter_by(status=0).all())

