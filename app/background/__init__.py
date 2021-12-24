from flask import Blueprint

bp = Blueprint('background', __name__)

from app.background import routes
