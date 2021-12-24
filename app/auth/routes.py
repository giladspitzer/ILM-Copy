from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, MoreInfoRegistration, ResetPasswordForm, \
    ResetPasswordRequestForm, EditProfileForm, PartnershipForm, RecruiterRegistrationForm, DeleteProfileForm
from app.models import User, Industry, Experience, Country, RecruitingAgency, Recruiter, MailActivity
from app.auth.emails import send_password_reset_email, send_email_confirm_registration, \
    send_email_confirm_password_reset, send_email_confirm_new_email, send_email_edit_profile_changes,\
    send_email_partnership_received, send_email_devs_new_partnership, \
    send_email_account_deletion_confirmed, send_email_confirm_recruiter_registration
from app.partnership.emails import send_email_new_recruiter_admin
from datetime import datetime, timedelta
from app.auth.tasks import check_entered_location


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        if current_user.completed < 2:
            g.more_info_registration = MoreInfoRegistration()
    else:
        g.registration_form = RegistrationForm()

    if '.php' in request.path or 'readme.html' in request.path or '/user/login' in request.path:
        return render_template('main/intruder.html')


@bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    else:
        return render_template('auth/register.html', title='Register', special=False)


@bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.verify_email_confirmation_token(token)
    if not user:
        flash('Could not confirm account. Please try again.')
        return redirect(url_for('main.index'))
    else:
        if not user.email_verified:
            user.email_verified = True
            db.session.commit()
            flash('Your email address has been verified')
            login_user(user, remember=False)
            if user.intended_mentor:
                return redirect(url_for('main.sessions_mentor'))
            else:
                return redirect(url_for('main.user', username=user.username))
        else:
            flash('An error has occurred.')
            return redirect(url_for('main.index'))


@bp.route('/confirm_recruiter/<token>', methods=['POST', 'GET'])
def confirm_recruiter(token):
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('auth.confirm_recruiter', token=token))
    recruiter = Recruiter.verify_confirmation_token(token)
    if not recruiter:
        flash('Confirmation link expired. Please contact your admin or email us for further support.')
        return redirect(url_for('main.index'))
    user = recruiter.user
    if user.completed < 2:
        user.created = datetime.utcnow()
        form = RecruiterRegistrationForm()
        form.industry_interest.choices = [(industry.id, industry.title) for industry in Industry.query.all()]
        form.industry_interest.choices.insert(0, (0, 'Please select an industry'))
        for choice in form.industry_interest:
            choice.render_kw = {'data-tokens': str(choice.label.text)}
        if user.position_title is not None:
            form.position_title.data = user.position_title
            form.position_title.render_kw = {'disabled': '', 'admin': ''}
        if user.experience_id is not None:
            form.experience.data = user.experience_id
            form.experience.render_kw = {'disabled': '', 'admin': ''}
        form.experience.choices = [(experience.id, experience.title) for experience in Experience.query.all()]
        if form.is_submitted():
            # ensure password constraints
            if len(form.password.data) < 1 or len(form.password.data) > 128:
                flash('Your password must be between 1 and 128 characters')
                return redirect(url_for('auth.confirm_recruiter', token=token))
            # ensure password matches
            if '@' in form.username.data or ' ' in form.username.data:
                flash('No spaces or ampersands allowed in username')
                return redirect(url_for('auth.confirm_recruiter', token=token))
            user_by_username = User.query.filter_by(username=form.username.data).first()
            if user_by_username is not None and user_by_username != user:
                flash('The username "' + str(form.username.data) + '" is already in use. Please enter a different one.')
                return redirect(url_for('auth.confirm_recruiter', token=token))
            if recruiter.admin == 2:
                user.username = str(form.username.data)
                user.position_title = str(form.position_title.data)
                user.experience_id = int(form.experience.data)
                recruiter.industry_interest_id = int(request.form.get('industry_interest'))
                user.password_length = len(form.password.data) * '*'
                user.set_password(form.password.data)
            else:
                user.username = str(form.username.data)
                recruiter.industry_interest_id = int(request.form.get('industry_interest'))
                user.password_length = len(form.password.data) * '*'
                user.set_password(form.password.data)
            recruiter.add_first_search()
            user.completed = 2
            user.email_verified = True
            user.recruiter.status = 1
            login_user(user)
            db.session.commit()
            admins = [x.user.email for x in recruiter.agency.recruiters.filter_by(admin=(1 or 2)).all()]
            send_email_confirm_recruiter_registration(user)
            send_email_new_recruiter_admin(admins, recruiter)
            return redirect(url_for('main.user', username=user.username))
    else:
        flash('Account Already Confirmed!')
        return redirect(url_for('main.index'))
    return render_template('auth/recruiter_registration.html', form=form)


# @bp.route('/confirm_partnership_inquiry/<token>', methods=['POST', 'GET'])
# def confirm_partnership_inquiry(token):
#     agency = RecruitingAgency.verify_confirmation_token(token)
#     if not agency:
#         flash('Confirmation link expired. Please try submitting another request for a partnership.')
#         return redirect(url_for('auth.partnership_inquiry'))
#     if agency.status < 1:
#         agency.status = 1
#         db.session.commit()
#         send_email_partnership_confirmed(agency)
#         send_email_devs_new_partnership(agency)
#
#         flash(
#             'Thank you for for confirming your request to to partner with ILMJTCV. We will be in touch with you as we review your application.')
#     else:
#         flash('Your request has already been confirmed. We will be in touch with you as we review your application.')
#     return redirect(url_for('main.index'))


@bp.route('/partnership_inquiry', methods=['GET'])
def partnership_inquiry():
    if current_user.is_authenticated:
        flash('You must logout to view the partnership inquiry page.')
        return redirect(url_for('main.index'))
    form = PartnershipForm()
    return render_template('auth/partnership_inquiry.html', form=form)


@bp.route('/cancel_partnership_inquiry/token', methods=['POST', 'GET'])
def cancel_partnership_inquiry(token):
    agency = RecruitingAgency.verify_confirmation_token(token)
    if not agency:
        flash('Confirmation link expired. Please try submitting another request for a partnership.')
        return redirect(url_for('auth.partnership_inquiry'))
    if agency.status < 1:
        agency.delete_agency()
        flash('We have withdrawn your request to partner with ILMJTCV. Feel free to submit another request anytime!')
    else:
        flash('Your request has already been confirmed. We will be in touch with you as we review your application.')
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        last = MailActivity.query.filter_by(user_id=current_user.id, type=2).order_by(
            MailActivity.timestamp.desc()).first()
        # print(last)
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
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            last = MailActivity.query.filter_by(user_id=user.id, type=2).order_by(
                MailActivity.timestamp.desc()).first()
            if last is not None and last.timestamp + timedelta(minutes=5) <= datetime.utcnow():
                user.password_reset_state = True
                db.session.commit()
                send_password_reset_email(user)
                flash('Check your email for the instructions to reset your password')
            else:
                user.password_reset_state = True
                db.session.commit()
                send_password_reset_email(user)
                flash('Check your email for the instructions to reset your password')
            return redirect(url_for('auth.login'))
        else:
            flash('No user associated with that email')
            return redirect(url_for('auth.register'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Reset link expired. Please try resetting your password again.')
        return redirect(url_for('main.index'))
    if not user.password_reset_state:
        flash('You have already reset your password.')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.email_verified = True
        user.set_password(form.password.data)
        user.password_reset_state = False
        db.session.commit()
        login_user(user, remember=False)
        send_email_confirm_password_reset(user)
        flash('Your password has been reset')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/confirm_account_deletion/<token>', methods=['POST', 'GET'])
def confirm_account_deletion(token):
    user = User.verify_account_deletion_token(token)
    if not user:
        flash('Something went wrong. If the problem persists please request an account deletion again.')
        return redirect(url_for('main.index'))
    else:
        form = DeleteProfileForm()
        if form.validate_on_submit():
            flash('Account successfully deleted')
            send_email_account_deletion_confirmed(user)
            logout_user()
            user.delete_user(form.reason.data)
            return redirect(url_for('main.contact'))
        return render_template('auth/account_deletion_confirm.html', form=form)

@bp.route('/unsubscribe')
@login_required
def unsubscribe():
    status = current_user.unsubscribe()
    if not status:
        flash('You are unable to edit your email preferences with a recruiter account.')
    else:
        flash('You have been unsubscribed from all involuntary email communication.')
    return redirect(url_for('main.index'))

@bp.route('/toggle_subscription')
@login_required
def toggle_subscription():
    if current_user.unsubscribed:
        status = current_user.resubscribe()
        if not status:
            flash('You are unable to edit your email preferences with a recruiter account. ')
    else:
        status = current_user.unsubscribe()
        if not status:
            flash('You are unable to edit your email preferences with a recruiter account. ')
        else:
            flash('You have been unsubscribed from all involuntary email communication.')
    return redirect(url_for('main.index'))