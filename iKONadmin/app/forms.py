# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField
from wtforms.validators import Email, DataRequired


# login and registration

class LoginForm(FlaskForm):
    username = StringField('Username', id='username_login', validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login', validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username', id='username_create', validators=[DataRequired()])
    email = StringField('Email', id='email_create', validators=[DataRequired(), Email()])
    password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])


class DeployForm(FlaskForm):
    project_name = StringField('Project Name', id='projectName', validators=[DataRequired()])
    deploy_name = StringField('Deployment Name', id='deploymentName', validators=[DataRequired()])
    entry_code_msg = 'The entry code should contain lower-case letters only without any spaces.'
    entry_code = StringField('Entry Code', id='entryCode', validators=[DataRequired()])
    location_list = TextAreaField('Location List', id='locationList', validators=[DataRequired()])
    language_select = SelectField('Language', id='languagesSelect')
    end_date = DateField('End Date', format='%m/%d/%Y', id='endDate')
    gamification_select = SelectField('Gamification', id='gamificationSelect')
    start_date = DateField('Start Date', format='%m/%d/%Y', id='startDate')
    sat_select = SelectField('Satellite Source', id='satSelect')
    wea_select = SelectField('Weather Station Source', id='weaSelect')
