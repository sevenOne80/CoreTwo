from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')
    submit = SubmitField('login')


class RegisterForm(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('last_name', validators=[DataRequired(), Length(max=64)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    password2 = PasswordField('confirm_password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    gdpr_consent = BooleanField('gdpr_consent', validators=[DataRequired()])
    submit = SubmitField('register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered')


class ResetRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('send_reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('confirm_password', validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField('reset_password')
