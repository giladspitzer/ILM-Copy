from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FileField, \
    DateField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, Length, url
from flask_wtf.file import FileAllowed
from app.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Name *', validators=[DataRequired(), Length(min=1, max=64)], render_kw={'maxlength': '64', 'id':'g_name'})
    username = StringField('Username *', validators=[DataRequired(), Length(max=64)], render_kw={'maxlength': '64', 'id':'g_username'})
    email = StringField('Email *', validators=[DataRequired(), Email(), Length(max=120)],
                        render_kw={'maxlength': '120', 'id':'g_email'})
    password = PasswordField('Password *', validators=[DataRequired(), Length(max=128)], render_kw={'maxlength': '128', 'id':'g_password'})
    mentor = BooleanField('Are you signing up as a mentor?')
    submit = SubmitField('Register!', render_kw={'disabled': '', 'id':'g_submit'})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None or '@' in username.data or ' ' in username.data:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class InitialRegistrationForm(FlaskForm):
    first = StringField('Name *', validators=[DataRequired(), Length(max=32)],render_kw={'maxlength':'32'} )
    last = StringField('', validators=[DataRequired(), Length(max=32)], render_kw={'maxlength':'32'})
    username = StringField('Username *', validators=[DataRequired(), Length(max=64)], render_kw={'maxlength':'64'})
    email = StringField('Email *', validators=[DataRequired(), Email(), Length(max=120)], render_kw={'maxlength':'120'})
    password = PasswordField('Password *', validators=[DataRequired(), Length(max=128)], render_kw={'maxlength':'128'})
    password2 = PasswordField(
        'Repeat Password *', validators=[DataRequired(), EqualTo('password')], render_kw={'maxlength':'128', 'disabled':''})
    country = SelectField('Country *', choices=[], validators=[InputRequired()], coerce=int)
    zip = StringField('Zip Code *')
    city = StringField('City *',  validators=[Length(max=32)])
    next = SubmitField('Continue ->', render_kw={'disabled': ''})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None or '@' in username.data or ' ' in username.data:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class MoreInfoRegistration(FlaskForm):
    industry = SelectField('Industry *', choices=[], validators=[InputRequired()], coerce=int)
    country = SelectField('Country *', choices=[], validators=[InputRequired()], coerce=int)
    zip = IntegerField('Zip Code *')
    city = StringField('City *', validators=[Length(max=32)])
    # date = DateField('Last Employed *', format='%d/%m/%Y', validators=[DataRequired(message="DD%MM%YYYY")])
    submit = SubmitField('Submit', render_kw={'disabled':''})

# class MoreInfoRegistration(FlaskForm):
#     industry = SelectField('Industry *', choices=[], validators=[InputRequired()], coerce=int)
#     company_name = StringField('Company Name *', validators=[DataRequired()], render_kw={'maxlength':'64'})
#     position_title = StringField('Position Title *', validators=[DataRequired()], render_kw={'maxlength':'64'})
#     experience = SelectField('Years of Experience *', choices=[], validators=[InputRequired()], coerce=int)
#     day = SelectField('', choices=[], validators=[InputRequired()], coerce=int)
#     month = SelectField('', choices=[], validators=[InputRequired()], coerce=int)
#     year = SelectField('', choices=[], validators=[InputRequired()], coerce=int)
#     # date = DateField('Last Employed *', format='%d/%m/%Y', validators=[DataRequired(message="DD%MM%YYYY")])
#     next = SubmitField('Continue -->', render_kw={'disabled':''})


class ConfirmRegistration(FlaskForm):
    submit = SubmitField('Create Account')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)], render_kw={'maxlength':'128'})
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password'), Length(max=128)], render_kw={'maxlength':'128', 'disabled':''})
    submit = SubmitField('Reset Password', render_kw={'disabled':''})


class EditProfileForm(FlaskForm):
    name = StringField('Full Name *', validators=[DataRequired(), Length(max=64)], render_kw={'maxlength':'64'})
    username = StringField('Username *', validators=[DataRequired(), Length(max=64)], render_kw={'maxlength':'64'})
    email = StringField('Email *', validators=[DataRequired(), Email(), Length(max=120)], render_kw={'maxlength':'120'})

    country = SelectField('Country *', choices=[], validators=[InputRequired()], coerce=int)
    zip = StringField('Zip Code *')
    city = StringField('City *', validators=[Length(max=32)])

    submit = SubmitField('Submit', render_kw={'disabled':''})

    def validate_username(self, user_by_username, current_user):
        if user_by_username is not None and user_by_username != current_user:
            raise ValidationError('That username is already in use. Please enter a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResumeForm(FlaskForm):
    resume = FileField('Upload Resume', validators=[FileAllowed(['pdf'], message='PDF Uploads only!')], render_kw={'onchange': 'FileValidation()'})
    submit = SubmitField('Submit')


class PartnershipForm(FlaskForm):
    name = StringField('Your Name *', validators=[DataRequired(), Length(min=2, max=100)],render_kw={'maxlength':'100'} )
    email = StringField('Email *', validators=[DataRequired(), Email(), Length(max=120)], render_kw={'maxlength':'120'})
    company_name = StringField('Company Name *', validators=[DataRequired(), Length(min=3, max=100)], render_kw={'maxlength': '100'})
    company_website = StringField('Company Website *', validators=[DataRequired(), Length(min=5, max=100)],
                               render_kw={'maxlength': '100'})
    additional_info = TextAreaField('Additional Info', validators=[Length(min=5, max=150)], render_kw={
        "placeholder": "If you have any additional information that you would like to share with us, you may add it here.",
        'style': 'resize:none; height:100px; overflow: auto;', 'maxlength':'150','background':'none'})
    recaptcha = RecaptchaField(render_kw={'id': 'recaptcha-form'})
    submit = SubmitField('Submit', render_kw={'style':'float:right'})


class RecruiterRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password *', validators=[DataRequired(), Length(max=128)], render_kw={'maxlength': '128'})
    password2 = PasswordField(
        'Repeat Password *', validators=[DataRequired(), EqualTo('password')],
        render_kw={'maxlength': '128', 'disabled': ''})
    position_title = StringField('Position Title *', validators=[DataRequired()], render_kw={'maxlength': '64'})
    experience = SelectField('Years of Experience *', choices=[], validators=[InputRequired()], coerce=int)
    industry_interest = SelectField('Industry Interest *', choices=[], validators=[InputRequired()], coerce=int)
    submit = SubmitField('Save Profile', render_kw={'disabled': ''})

class DeleteProfileForm(FlaskForm):
    reason = TextAreaField('Reason for deleting', render_kw={
        "placeholder": "Please let us know why you are deleting your account and if there is anything we can improve on that would make you come back. (optional)",
        'style': 'resize:none; height:100px; overflow: auto;', 'maxlength': '150', 'background': 'none'})
    # recaptcha = RecaptchaField(render_kw={'id': 'recaptcha-form'})
    submit = SubmitField('Submit', render_kw={'style': 'text-align:center'})