from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes, ajax_get, ajax_post
