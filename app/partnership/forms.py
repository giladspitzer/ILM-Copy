from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, InputRequired


class RecruiterSearchForm(FlaskForm):
    title = StringField('Title *', validators=[DataRequired()], render_kw={'placeholder':'Title your search'})
    description = TextAreaField('Description', render_kw={'maxlength':'140',"placeholder":"You may add any additional notes for yourself or for your colleagues about this search here", 'style':'height:75px;resize:none'
                                                                                                                                                              ''})
    industry = SelectField('Industry *', choices=[], validators=[DataRequired()], coerce=int)
    # experience = SelectField('Experience *', choices=[], validators=[DataRequired()], coerce=int)
    # country = SelectField('Country *', choices=[], validators=[InputRequired()], coerce=int)
    city = StringField('City *', render_kw={'placeholder':'City that the position you are filling is located'})
    public = BooleanField('Public')
    submit = SubmitField('Add Search', render_kw={'disabled':''})

