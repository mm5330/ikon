from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email
import app.database as db


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    entry_code = StringField('Entry Code', validators=[DataRequired()])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = db.getUserByUsername(username.data)
        if user:
            raise ValidationError('Please use a different username.')


    def validate_email(self, email):
        user = db.getUser(email.data)
        if user:
            raise ValidationError('Please use a different email address.')

    def validate_entry_code(self, entry_code):
        deploy = db.getDeployByCode(entry_code.data[:5])
        print("validate_entry_code: ", deploy)
        if deploy is None:
            raise ValidationError('Please enter a valid entry code.')
