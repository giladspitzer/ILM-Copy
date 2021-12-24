from flask import current_app
from flask_login import current_user
from app import db
from app.models import Country, City, State, ZipCode
import requests
import os
from PIL import ImageOps, Image
from boto3 import resource
from hashlib import md5
from SuperSaaS import Client
from datetime import datetime, timedelta
SCOPES = ['https://www.googleapis.com/auth/calendar']


def check_location(input):
    """Builds dictionary of user location data with 5 components if city entered and 6 components if zip entered.
    Input is the form.zip.data or form.city.data data. It is sent to the google map geo-coding API."""
    ## current_app.config.get('GOOGLE_API')
    params = {'key': 'current_app.config.get('GOOGLE_API')', 'address': input}
    r = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
    if r.status_code != 200:
        print(r)
    items = {}
    if len(r.json()['results']) > 0:
        results = r.json()['results'][0]['address_components']
        for i in results:
            if i['types'][0] == 'postal_code':
                items['postal'] = i['long_name']
            elif i['types'][0] == 'locality' or 'sublocality' in i['types']:
                items['city'] = i['long_name']
            elif i['types'][0] == 'administrative_area_level_1':
                items['state'] = [i['long_name'], i['short_name']]
            elif i['types'][0] == 'country':
                items['country'] = [i['long_name'], i['short_name']]
        location = r.json()['results'][0]['geometry']['location']
        items['lat'] = location['lat']
        items['lng'] = location['lng']
    return items


def add_locations(depth, data):
    """This function accepts the user-codes data and modifies their location preferences based on it. It will
    add locations to the database before assigning them if necessary. Returns dictionary of location id's so
    adding user function does not have to query."""
    # check country
    if Country.query.filter_by(code=data['country'][1]).count() > 0:
        user_country = Country.query.filter_by(code=data['country'][1]).first().id
    else:
        c = Country(name=data['country'][0], code=data['country'][1])
        db.session.add(c)
        user_country = Country.query.filter_by(code=data['country'][1]).first().id

    # check state
    if State.query.filter_by(name=data['state'][0]).count() > 0:
        user_state = State.query.filter_by(name=data['state'][0]).first().id
    else:
        s = State(name=data['state'][0], code=data['state'][1], country_id=user_country)
        db.session.add(s)
        user_state = State.query.filter_by(name=data['state'][0]).first().id

    # check city
    if City.query.filter_by(name=data['city'], state_id=user_state).count() > 0:
        user_city = City.query.filter_by(name=str(data['city']), state_id=user_state).first().id
    else:
        c = City(name=data['city'], state_id=user_state, country_id=user_country, lat=data['lat'], long=data['lng'])
        db.session.add(c)
        user_city = City.query.filter_by(name=data['city'], state_id=user_state).first().id
    if depth == 4:
        # check zip
        if ZipCode.query.filter_by(name=data['postal']).count() > 0:
            user_zip = ZipCode.query.filter_by(name=data['postal']).first().id
        else:
            z = ZipCode(name=data['postal'], city_id=user_city, state_id=user_state, country_id=user_country,
                        lat=data['lat'], long=data['lng'])
            db.session.add(z)
            user_zip = ZipCode.query.filter_by(name=int(data['postal'])).first().id
        return {'country': user_country, 'state': user_state, 'city': user_city, 'zip': user_zip}
    else:
        return {'country': user_country, 'state': user_state, 'city': user_city, 'zip': None}


def resize_images(path, type, user):
    for i in current_app.config['SIZES']:
        image = Image.open(path)
        new_image = image.convert('RGB')
        new_image = ImageOps.fit(new_image, (i, i), Image.ANTIALIAS)
        if type == 'user':
            img = 'app/static/uploads/user_img' + str(i) + '.jpg'
            name = 'user_img'
        else:
            img = 'app/static/uploads/r_img' + str(i) + '.jpg'
            name = 'accnt_img'
        new_image.save(img)
        upload_file(file=img, user=user, bucket=type, extension='image/jpg', name=name, size=i)
        os.remove(img)
    os.remove(path=path)


def upload_file(file, user, bucket, extension, name, size=None):
    # extension = 'image/jpg'
    # size = int
    # name = 'user_img
    # bucket = user or partner
    s3 = resource('s3', region_name='us-east-1',
                  aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                  aws_secret_access_key='current_app.config.get('AWS_SECRET')')
    if bucket == 'user':
        folder = str(md5(str(user.id).encode('utf-8')).hexdigest())
        b = 'ilmjtcv-user-static-files'
    elif bucket == 'events':
        folder = 'events'
        b = 'ilmjtcv-other'
    elif bucket == 'speakers':
        folder = 'events/speakers'
        b = 'ilmjtcv-other'
    elif bucket == 'news':
        folder = 'news'
        b = 'ilmjtcv-other'
    else:
        folder = str(md5(str(user.recruiter.agency_id).encode('utf-8')).hexdigest())
        b = 'ilmjtcv-recruiting-agencies'
    if size is not None:
        location = folder + '/' + name + str(size) + '.' + str(extension).split('/')[1]
    else:
        location = folder + '/' + name + '.' + str(extension).split('/')[1]
    s3.meta.client.upload_file(file, b, location, ExtraArgs={'ACL': 'public-read', 'ContentType': extension})

    return folder


def delete_file(bucket, user, extension, name):
    """This function accepts a bucket and filename and then queries S3 to delete whatever specified"""
    s3 = resource('s3', region_name='us-east-1',
                  aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                  aws_secret_access_key='current_app.config.get('AWS_SECRET')')
    if bucket == 'user':
        folder = str(md5(str(user.id).encode('utf-8')).hexdigest())
        b = 'ilmjtcv-user-static-files'
    else:
        folder = str(md5(str(user.recruiter.agency_id).encode('utf-8')).hexdigest())
        b = 'ilmjtcv-recruiting-agencies'
    obj = s3.Object(b, folder + '/' + name + '.' + str(extension).split('/')[1])
    obj.delete()


def available_slots(start=None, end=None):
    link = 'https://www.supersaas.com/api/free/509710.json?from=2020-07-28%2015:00:00&api_key=your_api_key&full=true'.replace('your_api_key', current_app.config['SSS_API_KEY'])
    return requests.get(link).content.decode('UTF-8')



