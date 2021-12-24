from flask import render_template
from app import db
from app.errors import bp
from flask import request, flash, redirect, url_for
from flask_login import current_user
from app.errors.emails import send_error_email

@bp.errorhandler(404)
def not_found_error(error):
    before = request.path
    if before is not None:
        if '/user/' in before:
            flash('The requested user does not exist')
            if current_user.is_authenticated:
                return redirect(url_for('main.user', username=current_user.username))
            else:
                return redirect(url_for('main.index'))
        elif '/forum/' in before:
            flash('The requested forum does not exist')
            return redirect(url_for('main.chat'))
    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    before = request.path
    if before is not None:
        if current_user.is_authenticated:
            send_error_email(current_user.username, before)
        else:
            send_error_email('anynon', before)
    db.session.rollback()
    return render_template('errors/500.html'), 500

