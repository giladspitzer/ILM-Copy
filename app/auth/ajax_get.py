from flask import render_template, flash, redirect, url_for, request, g
from flask_login import logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, MoreInfoRegistration, ResetPasswordRequestForm, \
    EditProfileForm, PartnershipForm
from app.models import MailActivity
from app.auth.emails import send_password_reset_email
from datetime import datetime, timedelta


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        if current_user.completed < 2:
            g.more_info_registration = MoreInfoRegistration()
    else:
        g.registration_form = RegistrationForm()


@bp.route('/register_', methods=['GET'])
def register_():
    if current_user.is_authenticated:
        return {'html': render_template('main/hompepage.html'), 'title': 'ILMJTCV', 'url': '/'}
    else:
        return {'html': render_template('auth/register.html', title='Register', j=0, r=0, special=False), 'title': 'Register', 'url': '/auth/register'}


@bp.route('/login_', methods=['GET'])
def login_():
    if current_user.is_authenticated:
        return {'html': render_template('main/hompepage.html'), 'title': 'ILMJTCV', 'url': '/'}
    else:
        form = LoginForm()
        return {'html': render_template('auth/login.html', form=form), 'title': 'Login', 'url': '/auth/login'}


@bp.route('/partnership_inquiry_', methods=['GET'])
def partnership_inquiry_():
    if current_user.is_authenticated:
        flash('You must logout to view the partnership inquiry page.')
        return redirect(url_for('main.index'))
    form = PartnershipForm()
    return {'html': render_template('auth/partnership_inquiry.html', form=form), 'title': 'Partner With Us', 'url': '/auth/partnership_inquiry'}


@bp.route('/reset_password_request_', methods=['GET'])
def reset_password_request_():
    if current_user.is_authenticated:
        last = MailActivity.query.filter_by(user_id=current_user.id, type=2).order_by(
            MailActivity.timestamp.desc()).first()
        if last is not None and last.timestamp + timedelta(minutes=5) <= datetime.utcnow():
            current_user.password_reset_state = True
            db.session.commit()
            send_password_reset_email(current_user)
            flash('Check your email for the instructions to reset your password')
        else:
            current_user.password_reset_state = True
            db.session.commit()
            send_password_reset_email(current_user)
            flash('Check your email for the instructions to reset your password')
        return redirect(request.referrer)
    form = ResetPasswordRequestForm()
    return {'html': render_template('auth/reset_password_request.html', title='Reset Password', form=form), 'title': 'Reset Password',
            'url': '/auth/reset_password_request'}

