from flask import flash, redirect, url_for, request, abort, current_app
from flask_login import current_user
from functools import wraps
from app import login



def restricted_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_recruiter:
            flash('This page is not accessible via your recruiter account')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper


def restricted_recruiter_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_recruiter:
            if current_user.recruiter.agency.status < 1:
                flash('This page is for org admins only.')
                return redirect(url_for('partnership.partner', id=current_user.recruiter.agency_id))
        return func(*args, **kwargs)

    return wrapper


def restricted_completed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.completed > 2:
            flash('Your account has been deactivated')
            return redirect(url_for('main.index'))
        if current_user.is_recruiter:
            if current_user.recruiter.status < 1:
                if current_user.recruiter.status == 0:
                    flash('You must reconfirm your email address browsing ILMJTCV.com')
                elif current_user.recruiter.status == -1:
                    flash('Your recruiter account has been deactivated')
                return redirect(url_for('main.user', username=current_user.username))
        return func(*args, **kwargs)

    return wrapper


def restricted_g(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != (724 or 727):
            abort(403)
        return func(*args, **kwargs)
    return wrapper


def restricted_recruiter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_recruiter:
            flash('This page is only accessible to registered recruiters')
            return redirect(url_for('main.user', username=current_user.username))
        else:
            if current_user.recruiter.agency.status < 3:
                if current_user.recruiter.admin == 2:
                    flash('In order to complete the registration, you must upload an image/logo to represent your company.')
        return func(*args, **kwargs)
    return wrapper
