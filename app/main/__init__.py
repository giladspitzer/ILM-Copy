from flask import Blueprint, current_app
# import os
bp = Blueprint('main', __name__)

# def make_celery():
#     os.system('source venv/bin/activate')
#     os.system('flask celery worker')
#     # current_app.config['SERVER_NAME'] = 'ilmjtcv.com'
#
# if 'SHELL' in os.environ.keys():
#     if os.environ['PATH'] == '/var/app/venv/staging-LQM1lest/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin':
#         print('hi')
#         bp.before_app_first_request(make_celery)

from app.main import routes, ajax_get, ajax_post
