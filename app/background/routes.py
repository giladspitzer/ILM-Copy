from app.models import User, JobListing, City, SavedSearch, RecruitingAgency, JobSavedSearch, \
    JobListingActivity, Notification, Recruiter, MailActivity, Appointment, AppointmentParticipantAssociations, Event, \
    MentorProfile
from flask import current_app, abort, redirect, url_for, flash
from boto3 import resource, client
from PIL import Image, ImageOps
import os
from hashlib import md5
from datetime import datetime, timedelta
import json
from geojson import Feature, Point, FeatureCollection
from app.background import bp
from app import db
from indeed import IndeedClient
from app.auth.emails import send_email_devs_new_partnership
from app.background.emails import send_email_map_update, send_email_partnership_approved, \
    send_email_new_candidates_found, send_email_partnership_approved_try_again, send_email_never_enrolled_recruiting,\
    send_email_partnership_rejected, send_email_appointment_join_mentor, send_email_appointment_join_mentee, \
    send_email_appointment_follow_up, send_email_event_reminder, send_email_recruiter_inactive, \
    send_email_mentor_inactive, send_email_mentor_incomplete, send_email_user_roundup, send_email_event_reminder_special
from app.tasks import upload_file, check_location, add_locations

def check_data(d, p):
    current_d = md5(str(datetime.strftime(datetime.utcnow(), '%m%d%Y')).encode('utf-8')).hexdigest()
    current_p = md5(str(current_app.config['BG_PASS']).encode('utf-8')).hexdigest()
    if current_d == d and current_p == p:
        return True
    else:
        return False


def upload_geojson(geojson):
    s3 = resource('s3', region_name='us-east-1',
                  aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                  aws_secret_access_key='current_app.config.get('AWS_SECRET')')
    geojson['updated'] = str(datetime.utcnow())
    content = json.dumps(geojson).encode("utf-8")
    s3.Object('ilmjtcv-geojson', 'geojson.json').put(Body=content, ContentType='application/json',
                                                     Bucket='ilmjtcv-geojson', Key='geojson.json',
                                                     ACL="public-read")


def update_job_listings_indeed(search, all=False):
    added = 0
    q = search.industries
    l = search.city_id
    r = search.proximity
    client = IndeedClient('current_app.config.get('INDEED_API')')
    if l is not None:
        loc = City.query.filter_by(id=int(l)).first_or_404()
        location = str(loc.name + ' ' + loc.state.name)
        city_id = int(l)
        country = str(City.query.filter_by(id=int(l)).first_or_404().country.code).lower()
        for industry in q:
            print('------Finding Jobs for ' + str(industry.title) + ') in ' + str(location))
            initial_params = {
                'q': industry.title,
                'l': location,
                'userip': "1.2.3.4",
                'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                'radius': str(r.title.split(' miles')[0]),
                'limit': '25',
                'co': country,
                'filter': '1',
                'latlong': '1'
            }
            search_response = client.search(**initial_params)
            if int(search_response['totalResults']) < 25 and int(search_response['totalResults']) > 0:
                pages = 1
            else:
                if int(search_response['totalResults']) > 350:
                    if all:
                        pages = 20
                    else:
                        pages = 14
                else:
                    pages = int(search_response['totalResults']) // 25
            print('---------' + str(search_response['totalResults']) + ' results (' + str(pages) + ' pages)')
            for i in range(1, int(pages + 1)):
                print('------------ Page: ' + str(i))
                params = {
                        'q': industry.title,
                        'l': location,
                        'userip': "1.2.3.4",
                        'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                        'radius': '50',
                        'limit': '25',
                        'start': str(i),
                        'co': country,
                        'latlong': '1'
                    }
                results = client.search(**params)
                for result in results['results']:
                    if JobListing.query.filter_by(job_key=str(result['jobkey']), city_id=int(city_id)).count() < 1:
                        if not result['expired']:
                            date = datetime.strptime(result['date'].split(' GMT')[0], '%a, %d %b %Y %H:%M:%S')
                            listing = JobListing(city_id=int(city_id), snippet=result['snippet'], indeed_url=result['url'],
                                                 date=date, location=result['formattedLocationFull'], source=1,
                                                 job_key=result['jobkey'], company=result['company'], job_title=result['jobtitle'])
                            if 'latitude' in result.keys() and 'longitude' in result.keys():
                                listing.lat = result['latitude']
                                listing.lon = result['longitude']
                            listing.industries.append(industry)
                            if not result['indeedApply']:
                                job_response = client.jobs(jobkeys=(str(listing.job_key), ''))
                                if len(job_response['results']) > 0:
                                    listing.apply_url = job_response['results'][0]['url']
                            db.session.add(listing)
                            if listing not in search.jobs:
                                added += 1
                                search.jobs.append(listing)
                    else:
                        listing = JobListing.query.filter_by(job_key=str(result['jobkey'])).first()
                        if industry not in listing.industries:
                            listing.industries.append(industry)
                        if 'latitude' in result.keys() and 'longitude' in result.keys():
                            listing.lat = result['latitude']
                            listing.lon = result['longitude']
                        if result['expired']:
                            listing.active = False
                            listing.date_no_longer_active = datetime.utcnow()
                        db.session.add(listing)
                        if listing not in search.jobs:
                            added += 1
                            search.jobs.append(listing)

                db.session.commit()
    else:
        for industry in q:
            print('------Finding Jobs for ' + str(industry.title) + ')')
            initial_params = {
                'q': industry.title,
                'userip': "1.2.3.4",
                'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                'limit': '25',
                'filter': '1',
                'latlong': '1'
            }
            search_response = client.search(**initial_params)
            if int(search_response['totalResults']) < 25 and int(search_response['totalResults']) > 0:
                pages = 1
            else:
                if int(search_response['totalResults']) > 350:
                    if all:
                        pages = 20
                    else:
                        pages = 14
                else:
                    pages = int(search_response['totalResults']) // 25
            print('---------' + str(search_response['totalResults']) + ' results (' + str(pages) + ' pages)')
            for i in range(1, int(pages + 1)):
                print('------------ Page: ' + str(i))
                params = {
                        'q': industry.title,
                        'userip': "1.2.3.4",
                        'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                        'limit': '25',
                        'start': str(i),
                        'latlong': '1'
                    }
                results = client.search(**params)
                for result in results['results']:
                    if JobListing.query.filter_by(job_key=str(result['jobkey'])).count() < 1:
                        if not result['expired']:
                            date = datetime.strptime(result['date'].split(' GMT')[0], '%a, %d %b %Y %H:%M:%S')
                            location_data = check_location(result['formattedLocationFull'])  # check their entered data
                            if 'city' not in list(location_data.keys()):  # if no postal code then return redirect
                                city_id = None
                            if 'state' not in list(location_data.keys()):  # if no postal code then return redirect
                                city_id = None
                            else:
                                try:
                                    user_codes = add_locations(3, location_data)
                                    city_id = user_codes['city']
                                except:
                                    city_id = None
                            listing = JobListing(snippet=result['snippet'], indeed_url=result['url'],
                                                 date=date, location=result['formattedLocationFull'], source=1,
                                                 job_key=result['jobkey'], company=result['company'], job_title=result['jobtitle'],
                                                 city_id=city_id)
                            if 'latitude' in result.keys() and 'longitude' in result.keys():
                                listing.lat = result['latitude']
                                listing.lon = result['longitude']
                            listing.industries.append(industry)
                            if not result['indeedApply']:
                                job_response = client.jobs(jobkeys=(str(listing.job_key), ''))
                                if len(job_response['results']) > 0:
                                    listing.apply_url = job_response['results'][0]['url']
                            db.session.add(listing)
                            if listing not in search.jobs:
                                added += 1
                                search.jobs.append(listing)
                    else:
                        listing = JobListing.query.filter_by(job_key=str(result['jobkey'])).first()
                        if industry not in listing.industries:
                            listing.industries.append(industry)
                        if 'latitude' in result.keys() and 'longitude' in result.keys():
                            listing.lat = result['latitude']
                            listing.lon = result['longitude']
                        if result['expired']:
                            listing.active = False
                            listing.date_no_longer_active = datetime.utcnow()
                        db.session.add(listing)
                        if listing not in search.jobs:
                            added += 1
                            search.jobs.append(listing)
                db.session.commit()
    return added


@bp.route('/update_imgs/<date>/<password>')
def update_img_sizes(date, password):
    check = check_data(date, password)
    if check:
        s3 = resource('s3', region_name='us-east-1',
                      aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                      aws_secret_access_key='current_app.config.get('AWS_SECRET')')
        bucket = s3.Bucket('ilmjtcv-user-static-files')
        for user in User.query.all():
            if user.img:
                sizes = []
                for obj in bucket.objects.filter(Prefix=user.directory):
                    if 'img' in str(obj.key).split('/')[1]:
                        main = str(obj.key)
                        sizes.append(int(str(obj.key).split('/')[1].split('.')[0].split('_img')[1]))
                if len(sizes) > 0 and len(sizes) != len(current_app.config['SIZES']):
                    additions = list(set(current_app.config['SIZES']) - set(sizes))
                    print(user.username, '--', additions)
                    if len(additions) > 0:
                        s3 = client('s3', region_name='us-east-1',
                                    aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                                    aws_secret_access_key='current_app.config.get('AWS_SECRET')')
                        path = 'app/static/uploads/' + str(user.username) + '.jpg'
                        with open(path, 'wb') as f:
                            s3.download_fileobj('ilmjtcv-user-static-files', main, f)
                        for a in additions:
                            image = Image.open(path)
                            new_image = image.convert('RGB')
                            new_image = ImageOps.fit(new_image, (a, a), Image.ANTIALIAS)
                            img = 'app/static/uploads/user_img' + str(a) + '.jpg'
                            new_image.save(img)
                            upload_file(file=img, user=user, bucket='user', extension='image/jpg', name='user_img', size=a)
                            os.remove(img)
                        os.remove(path=path)
        return redirect(url_for('main.index'))
    else:
        return abort(403)


@bp.route('/update_geojson/<date>/<password>')
def update_geojson(date, password):
    check = check_data(date, password)
    if check:
        collection = []
        # sidebar = []
        users = User.query.filter_by(completed=2, is_recruiter=False).all()
        for user in users:
            if user.zip_code_id is not None:
                coordinates = (user.zip_code.long, user.zip_code.lat)
            else:
                coordinates = (user.city.long, user.city.lat)
            feature = Feature(geometry=Point(coordinates), properties={'id': str(user.id)})
            collection.append(feature)
            # if user.city_id not in [x['id'] for x in sidebar]:
            #     if user.city.country_id == 235:
            #         display_name = str(user.city.name) + ' (' + str(user.state.code) + ')'
            #     else:
            #         display_name = str(user.city.name) + ' (' + str(user.country.name) + ')'
            #     sidebar.append({'id': user.city_id,
            #                     'count': 1,
            #                     'display_name': display_name,
            #                     'lat':City.query.filter_by(id=user.city_id).first().lat,
            #                     'lon':City.query.filter_by(id=user.city_id).first().long})
            # else:
            #     for x in sidebar:
            #         if x['id'] == user.city_id:
            #             x['count'] += 1
        # cities = ['Chicago (IL)', 'Atlanta (GA)', 'Kansas City (MO)', 'Philadelphia (PA)', 'Bangor (ME)',
        #           'Big Horn County (MT)', 'Phoenix (AZ)', 'Clifton (ID)', 'Omaha (NE)', 'Louisville (KY)',
        #           'Medford (OR)', 'Amarillo (TX)', 'Winnipeg (Canada)', 'Edmonton (Canada)', 'Quesnel (Canada)',
        #           'Ottawa (Canada)', 'Hearst (Canada)']
        # numbers = [327, 128, 293, 111, 85, 330, 122, 98, 435, 128, 214, 158, 214, 387, 91, 120, 217]
        # coordinates = [(41.8781, -87.6298), (33.7490, -84.3880), (39.0997, -94.5786), (39.9526, -75.1652),
        #                (44.8016, -68.7712), (45.3497, -107.2716), (33.4484, -112.0740), (42.1899, -112.0080),
        #                (41.2565, -95.9345), (38.2527, -85.7585), (42.3265, -122.8756), (35.2220, -101.8313),
        #                (49.8951, -97.1384), (53.5461, -113.4938), (52.9817, -122.4949), (45.4215, -75.6972),
        #                (49.6880, -83.6670)]
        # for i in range(len(cities)):
        #     for j in range(0, numbers[i]):
        #         coordinatesx = (coordinates[i][1], coordinates[i][0])
        #         feature = Feature(geometry=Point(coordinatesx), properties={'id': 12})
        #         collection.append(feature)
        #     sidebar.append({'id': 12,
        #                     'count': numbers[i],
        #                     'display_name': cities[i],
        #                     'lat': coordinates[i][0],
        #                     'lon': coordinates[i][1]})

        geojson = FeatureCollection(collection)
        # geojson['sidebar'] = sidebar
        upload_geojson(geojson)
        users = User.query.all()
        send_email_map_update(len(users))
        return redirect(url_for('main.index'))
    else:
        return abort(403)


@bp.route('/find_jobs_all/<date>/<password>')
def find_jobs_all(date, password):
    check = check_data(date, password)
    added = 0
    if check:
        for search in JobSavedSearch.query.filter_by(status=1).all():
            search.update_job_listings_local(10)
            if len(search.jobs) < 30:
                print('---- Adding Jobs for:' + str(search.title), len(search.jobs))
                added += update_job_listings_indeed(search, all=False)
                print('Added:', added)
                print(len(search.jobs))
                for job in search.jobs:
                    if JobListingActivity.query.filter_by(search_id=search.id, job_id=job.id).count() == 0:
                        a = JobListingActivity(job_id=job.id, search_id=search.id, status=0)
                        db.session.add(a)
                if added > 0:
                    for n in Notification.query.filter_by(type=1, specific_id=search.id, user_id=search.user_id, read=False).all():
                        n.read = True
                    db.session.commit()
                    n = Notification(user_id=search.user_id, title='New jobs found!',
                                     sub_title='Listings updated for ' + str(search.title), link='/job_search/' + str(search.id),
                                     type=1, specific_id=search.id)
                    db.session.add(n)
                    search.last_updated = datetime.utcnow()
                db.session.commit()
        return redirect(url_for('main.index'))
    else:
        return abort(403)


@bp.route('/find_jobs_all_hakol/<date>/<password>')
def find_jobs_all_hakol(date, password):
    check = check_data(date, password)
    added = 0
    if check:
        for search in JobSavedSearch.query.filter_by(status=1).all():
            added += search.update_job_listings_local(all=True)
            added += update_job_listings_indeed(search, all=True)
            for job in search.jobs:
                if JobListingActivity.query.filter_by(search_id=search.id, job_id=job.id).count() == 0:
                    a = JobListingActivity(job_id=job.id, search_id=search.id, status=0)
                    db.session.add(a)
            if added > 0:
                search.last_updated = datetime.utcnow()
                for n in Notification.query.filter_by(type=1, specific_id=search.id, user_id=search.user_id,
                                                      read=False).all():
                    n.read = True
                db.session.commit()
                n = Notification(user_id=search.user_id, title='New jobs found!',
                                 sub_title='Listings updated for ' + str(search.title),
                                 link='/job_search/' + str(search.id), type=1, specific_id=search.id)
                db.session.add(n)
            db.session.commit()
        return redirect(url_for('main.index'))
    else:
        return abort(403)


@bp.route('/activate_org/<id>')
def activate_org(id):
    r = RecruitingAgency.query.filter_by(id=int(id)).first_or_404()
    if r.status < 2:
        r.activate_org()
        recruiter = r.recruiters.filter_by(admin=2).first()
        send_email_partnership_approved(recruiter)
        flash('Success')
    return redirect(url_for('main.index'))


@bp.route('/reject_org/<id>')
def reject_org(id):
    r = RecruitingAgency.query.filter_by(id=int(id)).first_or_404()
    if r.status == 1:
        recruiter = Recruiter.query.filter_by(admin=2, agency_id=r.id).first()
        send_email_partnership_rejected(recruiter)
        r.reject_agency()
        flash('Success')
    return redirect(url_for('main.index'))


@bp.route('/find_candidates/<date>/<password>')
def find_candidates(date, password):
    check = check_data(date, password)
    if check:
        for search in SavedSearch.query.filter_by(status=1).all():
            results = search.apply_results()
            if results > 0:
                send_email_new_candidates_found(search)
                search.last_updated = datetime.utcnow()
        return redirect(url_for('main.index'))
    else:
        return abort(403)


@bp.route('/reconfirm_recruiters/<date>/<password>')
def reconfirm_recruiters(date, password):
    check = check_data(date, password)
    day = datetime.today().weekday()
    if day > 5:
        weekend = True
    else:
        weekend = False
    if check:
        if not weekend:
            print('Never followed up')
            agencies = RecruitingAgency.query.filter_by(status=2).all()
            for j in agencies:
                recruiter = j.recruiters.filter_by(admin=2).first()
                if recruiter.status == 0:
                    if j.date_requested < datetime.utcnow() - timedelta(days=1):
                        last = MailActivity.query.filter_by(user_id=recruiter.user_id, type=25).first()
                        if last is not None:
                            if last.timestamp <= datetime.utcnow() - timedelta(days=3):
                                    send_email_partnership_approved_try_again(recruiter)
        return redirect(url_for('main.index'))
    else:
        return abort(403)

# @bp.route('/never_enrolled_recruiting/<date>/<password>')
# def never_enrolled_recruiting(date, password):
#     check = check_data(date, password)
#     if check:
#         users = User.query.filter_by(completed=2, is_recruiter=False).filter(User.recruiter_visibility < 3,
#                                                          User.created <= datetime.utcnow() - timedelta(days=10)).all()
#         for user in users:
#             send_email_never_enrolled_recruiting(user)
#         return redirect(url_for('main.index'))
#     else:
#         abort(403)


@bp.route('/resend_confirm_org/<id>')
def resend_confirm_org(id):
    org = RecruitingAgency.query.filter_by(id=int(id)).first_or_404()
    if org.status == 1:
        send_email_devs_new_partnership(org)
        flash('success')
    flash('already verified')
    return redirect(url_for('main.index'))


@bp.route('/zgs')
def zgs():
    return str(User.query.filter_by(is_recruiter=False).count()) + ' & ' + str(User.query.filter_by(is_recruiter=True).count())


@bp.route('/send_appointment_check_ins/<date>/<password>')
def send_appointment_check_ins(date, password):
    check = check_data(date, password)
    if check:
        appointments = db.session.query(Appointment).join(AppointmentParticipantAssociations).filter(
            datetime.utcnow() + timedelta(minutes=5) >= Appointment.start_time,
            Appointment.start_time > datetime.utcnow()
        ).all()
        for appointment in appointments:
            if not appointment.check_in_sent:
                send_email_appointment_join_mentee(appointment.participants[0], appointment)
                send_email_appointment_join_mentor(appointment.mentor.user, appointment)
                appointment.check_in_sent = True
                db.session.commit()
        events = Event.query.filter(
            datetime.utcnow() + timedelta(minutes=5) >= Event.time_start,
            Event.time_start > datetime.utcnow()
        ).all()
        for event in events:
            if not event.invite_sent:
                rsvps = [x.user for x in event.rsvps.all()]
                admins = User.query.filter_by(admin=True).all()
                recents = []
                for i in admins:
                    if i not in rsvps:
                        rsvps.append(i)
                for user in User.query.filter_by(is_recruiter=False, unsubscribed=False).all():
                    if datetime.utcnow() - user.last_seen < timedelta(days=7) and user not in rsvps:
                        recents.append(user)
                for user in rsvps:
                    if user.last_sent_mail(218, timedelta(minutes=30)):
                        send_email_event_reminder(user, event)
                for user in recents:
                    if user.last_sent_mail(218, timedelta(minutes=30)):
                        send_email_event_reminder_special(user, event)
                event.invite_sent = True
                db.session.commit()

        return redirect(url_for('main.index'))
    else:
        abort(403)


@bp.route('/send_appointment_follow_up/<date>/<password>')
def send_appointment_follow_up(date, password):
    check = check_data(date, password)
    if check:
        appointments = db.session.query(Appointment).join(AppointmentParticipantAssociations).filter(
            datetime.utcnow() - timedelta(minutes=5) <= Appointment.end_time,
            Appointment.end_time < datetime.utcnow()
        ).all()
        for appointment in appointments:
            if not appointment.follow_up_sent:
                send_email_appointment_follow_up(appointment.participants[0], appointment)
                appointment.follow_up_sent = True
                db.session.commit()
        return redirect(url_for('main.index'))
    else:
        abort(403)

#
# @bp.route('/email_inactives/<date>/<password>')
# def email_inactives(date, password):
#     check = check_data(date, password)
#     if check:
#         for user in User.query.filter(datetime.utcnow()-timedelta(days=10) >= User.last_seen).all():
#             stats = {}
#             resume_views = user.get_resume_views()
#             stats['resume_views'] = int(resume_views * 1.2)
#             new_agencies = user.new_agencies()
#             stats['new_agencies'] = int(new_agencies * 1.2)
#             new_recruiters = user.new_recruiters()
#             stats['new_recruiters'] = int(new_recruiters * 1.2)
#             new_users_area = user.new_users_area()
#             stats['new_users_area'] = int(new_users_area * 1.2)
#             new_users_industry = user.new_users_industry()
#             stats['new_users_industry'] = int(new_users_industry * 1.2)
#             new_industry_jobs = user.new_industry_jobs()
#             stats['new_industry_jobs'] = int(new_industry_jobs * 1.2)
#             if MailActivity.query.filter_by(type=12, user_id=user.id).count() == 0:
#                 send_email_no_activity(user, stats)
#             else:
#                 if datetime.utcnow()-timedelta(days=10) >= MailActivity.query.filter_by(type=12, user_id=user.id).order_by(MailActivity.timestamp.desc()).first().timestamp:
#                     send_email_no_activity(user, stats)
#         return redirect(url_for('main.index'))
#     else:
#         return abort(403)
#
#
# @bp.route('/email_noncomplete/<date>/<password>')
# def email_noncomplete(date, password):
#     check = check_data(date, password)
#     if check:
#         for user in User.query.filter(User.completed < 2).all():
#             if MailActivity.query.filter_by(type=13, user_id=user.id).count() == 0:
#                 if datetime.utcnow() - timedelta(days=3) > user.last_seen:
#                     send_email_never_finished(user, '4 days')
#             else:
#                 if MailActivity.query.filter_by(type=13, user_id=user.id).count() < 2:
#                     if datetime.utcnow() - timedelta(days=6) > user.last_seen:
#                         send_email_never_finished(user, '24 hours')
#                 elif MailActivity.query.filter_by(type=13, user_id=user.id).count() >= 2:
#                     if datetime.utcnow() - timedelta(days=7) > user.last_seen:
#                         print('del--', user)
#                         send_email_user_deleted(user)
#                         db.session.delete(user)
#                         db.session.commit()
#         return redirect(url_for('main.index'))
#     else:
#         return abort(403)

@bp.route('/send_bg_emails')
def send_bg_emails():
    # Inactive Recruiters
    inactive_recruiters = db.session.query(User).join(Recruiter, (Recruiter.user_id == User.id)).filter(
        User.last_seen <= datetime.utcnow() - timedelta(weeks=2),
        Recruiter.status > 0,
        User.unsubscribed == False
    ).all()
    for i in inactive_recruiters:
        if i.last_sent_mail(500, timedelta(weeks=2)):
            send_email_recruiter_inactive(i)

    # Mentors YES Sign Up / No Appointments
    completed_mentors = db.session.query(User).join(MentorProfile, (MentorProfile.user_id == User.id)).filter(
        MentorProfile.status > 0,
        User.unsubscribed == False
    ).all()
    for i in completed_mentors:
        if Appointment.query.filter(Appointment.start_time >= datetime.utcnow(), Appointment.mentor_id == i.mentor_profile.id).count() == 0:
            if i.last_sent_mail(502, timedelta(weeks=2)):
                send_email_mentor_inactive(i)

    # Mentors NO Sign Up
    incomplete_mentors = User.query.filter_by(intended_mentor=True, unsubscribed=False).all()
    for i in incomplete_mentors:
        if MentorProfile.query.filter_by(user_id=i.id).count() == 0:
            if i.last_sent_mail(503, timedelta(days=5)):
                send_email_mentor_incomplete(i)

    # User Roundup
    roundups = User.query.filter_by(unsubscribed=False).all()
    for i in roundups:
        if i.last_sent_mail(501, timedelta(weeks=2)):
            send_email_user_roundup(i)
    return redirect(url_for('main.index'))
