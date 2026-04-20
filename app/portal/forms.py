from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, DateField, IntegerField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class IdentityForm(FlaskForm):
    national_number = StringField('national_number', validators=[
        DataRequired(), Length(min=11, max=15)
    ])
    birth_date = DateField('birth_date', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('continue')


class UploadExtractForm(FlaskForm):
    extract_file = FileField('extract_file', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF only')
    ])
    submit = SubmitField('analyse')


class InvestorProfileForm(FlaskForm):
    q1 = RadioField('q1_horizon', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', ''), ('5', '')
    ])
    q2 = RadioField('q2_objective', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', '')
    ])
    q3 = RadioField('q3_loss_tolerance', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', ''), ('5', '')
    ])
    q4 = RadioField('q4_reaction_drop', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', '')
    ])
    q5 = RadioField('q5_knowledge', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', '')
    ])
    q6 = RadioField('q6_experience', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', '')
    ])
    q7 = RadioField('q7_income_stability', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', '')
    ])
    q8 = RadioField('q8_savings_proportion', validators=[DataRequired()], choices=[
        ('1', ''), ('2', ''), ('3', ''), ('4', '')
    ])
    submit = SubmitField('continue')


class ProductSelectionForm(FlaskForm):
    product_id = SelectField('product_id', validators=[DataRequired()], coerce=int)
    amount = IntegerField('amount', validators=[DataRequired(), NumberRange(min=1000)])
    submit = SubmitField('continue')


class SignatureForm(FlaskForm):
    agree_terms = BooleanField('agree_terms', validators=[DataRequired()])
    agree_info = BooleanField('agree_info', validators=[DataRequired()])
    submit = SubmitField('sign_and_submit')
