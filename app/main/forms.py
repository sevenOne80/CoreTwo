from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=100)])
    email = StringField('email', validators=[DataRequired(), Email()])
    subject = StringField('subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('send')
