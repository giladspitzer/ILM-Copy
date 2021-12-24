from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, InputRequired
from flask_wtf.file import FileAllowed
from flask import request


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)], render_kw={"placeholder": 'Title your post', 'maxlength':'100', 'minlength':'5'})
    body = TextAreaField('Post', validators=[DataRequired(), Length(min=5, max=1800)], render_kw={"placeholder": 'Say something...', 'maxlength':'1800', 'minlength':'5'})
    submit = SubmitField('Submit', render_kw={'disabled': ''})


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(min=5, max=1800)], render_kw={"placeholder": 'Say something about this post...', 'maxlength':'1800', 'minlength':'5'})
    submit = SubmitField('Submit', render_kw={'disabled':''})


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class ComplaintForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "John Appleseed"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "your-email@example.com"})
    user = BooleanField('User', render_kw={'style': 'display:none'})
    body = TextAreaField('Message', validators=[DataRequired(), Length(min=5, max=500)], render_kw={"placeholder": "Tell us about an issue you've been having with our site. Please include the page you were viewingand what you were doing when you experienced the issue. Thanks for helping and allowing us to build a better product!",
                                                                                                    'style': 'resize:vertical; max-height: 250px; min-height: 115px; overflow: auto; height: 130px',
                                                                                                    'maxlength':'500'})
    recaptcha = RecaptchaField(render_kw={'id': 'recaptcha-form'})
    submit = SubmitField('Submit', render_kw={'style': 'float: right; text-align:center', 'class':'btn btn-primary btn-block'})


class ImageForm(FlaskForm):
    file = FileField('File', render_kw={'onchange':'FileValidation()'})
    submit = SubmitField('Submit')


class ImageFormMobile(FlaskForm):
    file = FileField('File', render_kw={'onchange': 'MobileFileValidation()', 'id':'mobile_file'})
    submit = SubmitField('Submit', render_kw={"id":"mobile_submit"})


class ReportPost(FlaskForm):
    body = TextAreaField('Report', validators=[DataRequired(), Length(min=5, max=350)], render_kw={
        "placeholder": "Please give us a reason for reporting this post. Include any particular language that may have caused you to report it.",
        'style': 'resize:none; max-height: 85px; min-height: 85px; overflow: auto; height: 85px',
       'maxlength':'350'})
    recaptcha = RecaptchaField(render_kw={'id': 'recaptcha-form'})
    submit = SubmitField('Submit',
                         render_kw={'style': 'float: right; text-align:center', 'class': 'btn btn-primary btn-block'})

class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField('', validators=[DataRequired(), Length(min=0, max=140)], render_kw={'placeholder':'Reply to this message thread...', 'style':'height:65px; overflow:auto; resize:none', 'maxlength':'140'})
    submit = SubmitField('Submit', render_kw={'style':'float:right; margin-top: 3px'})


class NewMessageForm(FlaskForm):
    recipients = StringField('Recipients', render_kw={'id': 'autocomplete'})
    recipients_list = StringField('', render_kw={'style': 'display:none'})
    subject =StringField('Subject', render_kw={'placeholder': 'What is this message about', 'maxlength':'140'}, validators=[DataRequired(), Length(min=1, max=140)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=140)],
                            render_kw={'placeholder': 'Your message....',
                                       'style': 'height:65px; overflow:auto; resize:none', 'maxlength':'140'})
    submit = SubmitField('Send', render_kw={'style': 'float:right; margin-top: 3px', 'disabled': ''})


class OptInRecruitersForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "John Appleseed", 'disabled':''})
    body = TextAreaField('Additional Info', validators=[Length(max=150)], render_kw={
        "placeholder": "If you have any additional information that you would like to share with the recruiters who will be reviewing your resume, you may add it here.",
        'style': 'resize:none; height:130px; overflow: auto;', 'maxlength':'150'})
    resume = FileField('Upload Resume*', validators=[DataRequired(), FileAllowed(['pdf'], message='PDF Uploads only!')],
                       render_kw={'onchange': 'FileValidation()'})
    recaptcha = RecaptchaField(render_kw={'id': 'recaptcha-form'})
    submit = SubmitField('Submit',
                         render_kw={'style': 'float: right; text-align:center', 'class': 'btn btn-primary btn-block'})


class JobFoundForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "John Appleseed"})
    body = TextAreaField('Additional Info', validators=[Length(max=150)], render_kw={
        "placeholder": "Please tell us about how you found the job using our site and whether it was through the job listings or a recruiter contact.",
        'style': 'resize:none; height:130px; overflow: auto;', 'maxlength': '150'})
    testimonial = BooleanField('Allow ILMJTCV to use your success story as a testimonial for marketing purposes.')
    submit = SubmitField('Submit',
                         render_kw={'style': 'float: right; text-align:center', 'class': 'btn btn-primary btn-block'})

class JobSavedSeaarch(FlaskForm):
    title = StringField('Title *', validators=[DataRequired()],
                        render_kw={'placeholder': 'Title your job search', 'maxlength': '80'})
    description = TextAreaField('Description', render_kw={'maxlength': '140',
                                                          "placeholder": "You may add any additional notes for yourself about this job search",
                                                          'style': 'height:75px;resize:none'
                                                                   ''})
    l_specific = BooleanField('Location Specific')
    city = StringField('City *', validators=[DataRequired(), Length(min=3, max=32)],
                       render_kw={'placeholder': 'City for your job search'})
    proximity = SelectField('Proximity *', choices=[], validators=[InputRequired()], coerce=int)
    submit = SubmitField('Add Search', render_kw={'disabled': ''})