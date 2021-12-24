from flask import Blueprint

bp = Blueprint('partnership', __name__)

from app.partnership import routes, ajax_post, ajax_get

