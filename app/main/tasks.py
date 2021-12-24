from flask import current_app
from app import db
from flask_login import current_user
from datetime import datetime
from app.models import City, Employer, Institution, \
    EmployerAssociations
import requests
from app.tasks import add_locations, check_location
import json
import base64


def extract_resume_data(path, filename):
    with open(path, "rb") as filePath:
        encoded_string = base64.b64encode(filePath.read())
    data64 = encoded_string.decode('UTF-8')
    headers = {'content-type': 'application/json'}

    body = """{"filedata":\"""" + data64 + """\","filename":\"""" + filename + """\","userkey":\"""" + \
           current_app.config['RCHILLI_KEY'] + """\",\"version\":\"""" + current_app.config['RCHILLI_VERSION'] \
           + """\",\"subuserid\":\"""" + current_app.config['RCHILLI_ID'] + """\"}"""

    response = requests.post(current_app.config['RCHILLI_API'], data=body, headers=headers)
    response2 = json.loads(response.text)
    data = response2["ResumeParserData"]

    adjectives = []
    for i in data['SegregatedSkill']:
        adjectives.append({'type': i['Type'], 'skill':i['Skill']})
    institutions = []
    for i in data['SegregatedQualification']:
        # print(i)
        institutions.append({'name': i['Institution']['Name'], 'city': i['Institution']['Location']['City']})
    employers = []
    for i in data['SegregatedExperience']:
        if i['IsCurrentEmployer'] == 'true':
            employers.append({'employer':i['Employer']['EmployerName'], 'start':i['StartDate'], 'end':'', 'is_current':'true', 'description':i['JobDescription']})
        else:
            employers.append({'employer':i['Employer']['EmployerName'], 'start':i['StartDate'], 'end':i['EndDate'], 'is_current':'false', 'description':i['JobDescription']})
    return {'adjectives':adjectives, 'institutions':institutions, 'employers':employers}


def add_institution(institution):
    city_name = City.query.filter_by(name=institution['city'])
    if city_name.count() == 0:
        data = check_location(str(institution['city']))
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            return 0
        user_codes = add_locations(3, data)
        city_id = user_codes['city']
    else:
        city_id = city_name.first().id
    institution_name = Institution.query.filter_by(name=institution['name'], city_id=city_id)
    if institution_name.count() == 0:
        i = Institution(name=institution['name'], city_id=city_id)
        db.session.add(i)
        db.session.commit()
    else:
        i = institution_name.first()
    if current_user.recruiting_profile not in i.users:
        i.users.append(current_user.recruiting_profile)
    else:
        return 0
    db.session.commit()
    return i.id


def add_employer(employer):
    employer_name = Employer.query.filter_by(name=employer['employer'])
    if employer_name.count() == 0:
        e = Employer(name=employer['employer'])
        db.session.add(e)
        db.session.commit()
        employer_id = e.id
    else:
        employer_id = employer_name.first().id
    associations = EmployerAssociations.query.filter_by(profile_id=current_user.recruiting_profile.id, employer_id=employer_id)
    if associations.count() == 0:
        if employer['is_current'] == 'true':
            try:
                start = datetime.strptime(employer['start'], '%m/%d/%Y')
            except:
                start = None
            a = EmployerAssociations(profile_id=current_user.recruiting_profile.id, employer_id=employer_id, start=start,
                                     is_current=True, job_description=employer['description'])
        else:
            try:
                start = datetime.strptime(employer['start'], '%m/%d/%Y')
            except:
                start = None
            try:
                end = datetime.strptime(employer['end'], '%m/%d/%Y')
            except:
                end = None
            a = EmployerAssociations(profile_id=current_user.recruiting_profile.id, employer_id=employer_id, start=start, end=end,
                                     is_current=False, job_description=employer['description'])
        db.session.add(a)
        db.session.commit()
        return a.id
    else:
        return 0


# def add_resume_data(data):
#     for skill in data['adjectives']:
#         print(skill)
#         type = SkillType.query.filter_by(name=skill['type'])
#         if type.count() == 0:
#             t = SkillType(name=skill['type'])
#             db.session.add(t)
#             db.session.commit()
#             type_id = t.id
#         else:
#             type_id = type.first().id
#         word = SkillWord.query.filter_by(type_id=type_id, name=skill['skill'])
#         if word.count() == 0:
#             s = SkillWord(type_id=type_id, name=skill['skill'])
#             db.session.add(s)
#             db.session.commit()
#             skill = s
#         else:
#             skill = word.first()
#         if current_user.recruiting_profile not in skill.users:
#             skill.users.append(current_user.recruiting_profile)
#         db.session.commit()
#     for employer in data['employers']:
#         print(employer)
#         add_employer(employer)
#     for institution in data['institutions']:
#         print(institution)
#         add_institution(institution)
